import argparse
from crawlers import ProductCrawler, save_to_file
from config.logging_config import setup_logging

CATEGORY_URL = "https://shopee.vn/Th%E1%BB%9Di-Trang-Nam-cat.11035567?page="


def main(args):
    setup_logging()
    if args.product:
        product_crawler = ProductCrawler()
        # product_crawler.find_product_urls(CATEGORY_URL)
        # save_to_file(product_crawler.product_urls, "data/product_urls.json")
        # print(f"Saved {len(product_crawler.product_urls)} product urls to product_urls.json")
        product_crawler.get_product_details("data/product_urls.json")
    elif args.comment:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", action="store_true")
    args = parser.parse_args()
    main(args)
