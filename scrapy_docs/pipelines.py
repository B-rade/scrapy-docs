# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3


class VisitUrlPipeline:
    def __init__(self, db):
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db=crawler.settings.get('DB'),
        )

    def open_spider(self, spider):
        self.con = sqlite3.connect(self.db)

    def process_item(self, item, spider):
        if item.get('visited_url') and item.get('id'):
            with self.con:
                self.con.execute(f"UPDATE urls SET visited = ? where id = ?;", (True, item['id']))
        return item

    def close_spider(self, spider):
        self.con.close()


class StoreImagePipeline:
    def __init__(self, db):
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db=crawler.settings.get('DB'),
        )

    def open_spider(self, spider):
        self.con = sqlite3.connect(self.db)
        try:
            with self.con:
                self.con.execute(f"""
                create table image_urls (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL, image_url TEXT NOT NULL);
                """)
        except sqlite3.OperationalError:
            pass

    def process_item(self, item, spider):
        if item.get('url') and item.get('img'):
            with self.con:
                self.con.execute(f"INSERT INTO image_urls(url, image_url) VALUES(?,?);", (item['url'], item['img']))
        return item

    def close_spider(self, spider):
        self.con.close()


class StoreUrlPipeline:
    def __init__(self, db):
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db=crawler.settings.get('DB'),
        )

    def open_spider(self, spider):
        self.con = sqlite3.connect(self.db)
        with self.con:
            self.con.execute(f"""
            create table urls (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL, visited INTEGER default 0);
            """)

    def process_item(self, item, spider):
        with self.con:
            self.con.execute(f"INSERT INTO urls(url, visited) VALUES(?,?);", (item['url'], False))
        return item

    def close_spider(self, spider):
        self.con.close()
