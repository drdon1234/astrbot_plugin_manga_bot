from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Nodes
from astrbot.core.star.filter.event_message_type import EventMessageType
from .crawler_module.cola_crawler import ColaCrawler
from .crawler_module.copy_crawler import CopyCrawler
import re
from typing import List

@register("astrbot_plugin_manga_bot", "drdon1234", "聚合漫画插件", "1.0")
class MangaBotPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.crawlers = {
            "cola": ColaCrawler(),
            "copy": CopyCrawler()
        }

    async def terminate(self):
        pass

    @staticmethod
    def parse_command(message: str) -> List[str]:
        cleaned_text = re.sub(r'@\S+\s*', '', message).strip()
        return [p for p in cleaned_text.split(' ') if p][1:]

    @filter.event_message_type(EventMessageType.ALL)
    async def manga_search_handler(self, event: AstrMessageEvent):
        match = re.search(r'.?搜(\w+)\s+(.*)', event.message_str)
        if not match:
            return
        website = match.group(1)
        if website not in self.crawlers:
            return
        params = match.group(2).strip().split()
        if not params:
            await event.send(event.plain_result("请提供搜索关键词"))
            return
        keyword = re.sub(r'[，,+]+', ' ', params[0])
        page = 1
        if len(params) > 1:
            try:
                page = int(params[1])
            except ValueError:
                await event.send(event.plain_result("页码必须是数字"))
                return
        await event.send(event.plain_result(f"漫画搜索机器人为您服务 ٩(｡•ω•｡)و 正在{website}平台搜索: {keyword}"))
        try:
            crawler = self.crawlers[website]
            result = await crawler.search_manga(keyword, page)
            await event.send(event.plain_result(result))
        except Exception as e:
            await event.send(event.plain_result(f"搜索出错: {str(e)}"))



