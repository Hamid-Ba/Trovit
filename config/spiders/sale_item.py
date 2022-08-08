import scrapy

class SaleItemSpider(scrapy.Spider):
    name = 'sale_item'
    allowed_domains = ['homes.trovit.com']
    start_urls = ['https://homes.trovit.com']

    def parse(self, response):
        # category = response.xpath('//ul[@class="lh-selector lh-property-deal-type"]/li/span')
        cities = response.xpath('//li[@data-test="location"]/a')
        for city in cities:
            name = city.xpath('.//text()').get()
            link = city.xpath('.//@href').get()

            yield scrapy.Request(url=link, callback=self.parse_city, meta={"city_name": name})

        next_sub_category = response.xpath(
            '//ul[@class="lh-selector lh-property-deal-type"]/li/following-sibling::li')

        if next_sub_category:
            category_a = next_sub_category.xpath('.//a')
            category_type = category_a.xpath('.//@data-test').get()
            type = category_type.split('-')[-1]

            category_link = category_a.xpath('.//@href').get()
            yield scrapy.Request(url=category_link, callback=self.parse)

        # Sale OR Rent
        next_category = response.xpath(
            '//ul[@class="lh-selector lh-deal-type"]/li/following-sibling::li')

        if next_category:
            categroy_a = next_category.xpath('.//a')
            category_type = categroy_a.xpath('.//text()').get()
            category_link = categroy_a.xpath('.//@href').get()

            yield scrapy.Request(url=category_link, callback=self.parse)

    def parse_city(self, response):
        items = response.xpath(
            '//div[@class="snippet-wrapper js-item-wrapper"]')
        city_name = response.request.meta["city_name"]

        for item in items:
            item_details = item.xpath('.//descendant::a[@class="rd-link"]')

            title = item_details.xpath(
                './/descendant::div[@class="item-title"]/span/text()').get()
            desc = item_details.xpath(
                './/descendant::div[@class="item-description"]/p/text()').get()
            price = item_details.xpath(
                './/descendant::span[@class="actual-price"]/text()').get()

            room_count = item_details.xpath(
                './/descendant::div[@class="item-property item-rooms"]/span/text()').get()
            bathroom_count = item_details.xpath(
                './/descendant::div[@class="item-property item-baths"]/span/text()').get()
            size_area = item_details.xpath(
                './/descendant::div[@class="item-property item-size"]/span/text()').get()

            published_date = item_details.xpath(
                './/descendant::span[@class="item-published-time"]/text()').get()

            # Specify is it belong today ?
            # gallery_tag = item.xpath('.//descendant::div[@class="left_tags"]/div/span/text()').get()

            # if published_date.__contains__("1 day ago") or published_date.__contains__("h"):
            # Compact Result
            res = {
                "city_name": city_name,
                "title": title,
                "desc": desc,
                "price": price,
                "date": published_date
            }
            # //a[@class='trovit-button no-background next']
            if room_count:
                res["room_count"] = room_count
            if bathroom_count:
                res["bathroom_count"] = bathroom_count
            if size_area:
                res["size_area"] = size_area

            yield res

        next_page = response.xpath('//a[@data-test="p-next"]/@href').get()

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_city, meta={"city_name": city_name})