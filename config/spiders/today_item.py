import scrapy


class TodayItemSpider(scrapy.Spider):
    name = 'today_item'
    allowed_domains = ['homes.trovit.com']
    start_urls = ['https://homes.trovit.com']

    # script = """
    #     function main(splash, args)
    #         splash.private_mode_enabled = false
    #         url = args.url
    #         assert(splash:go(url))
    #         assert(splash:wait(2))
    #         today = assert(splash:select_all('.js-filter-value'))
    #         today[28]:mouse_click()
    #         assert(splash:wait(2))
    #         splash:set_viewport_full()
    #         return splash:png()
    #     end
    # """

    def parse(self, response):
        cities = response.xpath('//li[@data-test="location"]/a')
        
        for city in cities:
            
            name = city.xpath('.//text()').get()
            link = city.xpath('.//@href').get()
            selected_sub = response.xpath('//ul[@class="lh-selector lh-property-deal-type"]/li/span/text()').get()
            # yield SplashRequest(url=link,callback=self.parse_city,endpoint="execute",args={"lua_source":self.script})
            yield scrapy.Request(url=link , callback=self.parse_city,meta = {"city_name" : name ,"selected_sub" : selected_sub})

        next_sub_category = response.xpath('//ul[@class="lh-selector lh-property-deal-type"]/li/following-sibling::li')

        if next_sub_category :
            category_a = next_sub_category.xpath('.//a')
            category_type = category_a.xpath('.//@data-test').get()
            type = category_type.split('-')[-1]
            category_link = category_a.xpath('.//@href').get()
            
            yield scrapy.Request(url=category_link, callback=self.parse)

        # # Sale OR Rent
        next_category = response.xpath('//ul[@class="lh-selector lh-deal-type"]/li/following-sibling::li')

        if next_category :
            categroy_a = next_category.xpath('.//a')
            category_type = categroy_a.xpath('.//text()').get()
            category_link = categroy_a.xpath('.//@href').get()

            yield scrapy.Request(url=category_link, callback=self.parse)
    
    

    def parse_city(self,response):
        the_alias = response.xpath("//strong[@class='qa-bc-current']/text()").get().lower()
        the_type = 1 # 1 For Home
        
        # finding id
        # the_script = response.xpath('//div[@class="feedback-modal__background modal_background js-feedback-modal-cancel"]/following::script/following::script/following::script/following::script/following::script/following::script/following::script/following::script').get()
        # the_geo_part = the_script.split('"geo_id":"')[1]
        # the_id = the_geo_part.split('"')[0]
        
        city_name = response.request.meta["city_name"]
        selected_sub = response.request.meta["selected_sub"]

        if selected_sub == "Land" : the_type = 10
        elif selected_sub == "Retail property" : the_type = 13
        elif selected_sub == "Foreclosures" : the_type = 18

        link = f'https://homes.trovit.com/cod.search_homes/type.{the_type}/what_d.{the_alias}/sug.0/isUserSearch.1/order_by.relevance/date_from.1'
        print(link)
        yield scrapy.Request(url = link,callback = self.parse_detail,meta = {"city_name" : city_name ,"selected_sub" : selected_sub})

    def parse_detail(self,response):
        items = response.xpath('//div[@class="snippet-wrapper js-item-wrapper"]')
        city_name = response.request.meta["city_name"]
        selected_sub = response.request.meta["selected_sub"]

        for item in items:
            item_details = item.xpath('.//descendant::a[@class="rd-link"]')

            title = item_details.xpath('.//descendant::div[@class="item-title"]/span/text()').get()
            desc = item_details.xpath('.//descendant::div[@class="item-description"]/p/text()').get()
            price = item_details.xpath('.//descendant::span[@class="actual-price"]/text()').get()

            room_count = item_details.xpath('.//descendant::div[@class="item-property item-rooms"]/span/text()').get()
            bathroom_count = item_details.xpath('.//descendant::div[@class="item-property item-baths"]/span/text()').get()
            size_area = item_details.xpath('.//descendant::div[@class="item-property item-size"]/span/text()').get()

            published_date = item_details.xpath('.//descendant::span[@class="item-published-time"]/text()').get()
            
            # Specify is it belong today ?
            # gallery_tag = item.xpath('.//descendant::div[@class="left_tags"]/div/span/text()').get()

            # if published_date.__contains__("1 day ago") or published_date.__contains__("h"):
                # Compact Result
            res = {
                "city_name": city_name,
                "title" : title,
                "desc" : desc,
                "price" : price,
                "date" : published_date
            }
            # //a[@class='trovit-button no-background next']
            if room_count:
                res["room_count"] = room_count
            if bathroom_count :
                res["bathroom_count"] = bathroom_count
            if size_area :
                res["size_area"] = size_area

            yield res

        next_page = response.xpath('//a[@data-test="p-next"]/@href').get()

        if next_page :
            yield scrapy.Request(url=next_page,callback = self.parse_city , meta = {"city_name" : city_name , "selected_sub" : selected_sub})