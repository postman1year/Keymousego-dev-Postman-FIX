from abc import ABCMeta, abstractmethod
from typing import List, Dict, Any
from loguru import logger
import json5


class JsonObject:
    def __init__(self, content: Dict[str, Any]):
        self.content = content
        self.next_object = None
        self.next_object_if_false = None


class Parser(metaclass=ABCMeta):
    # Simply get json object
    @staticmethod
    @abstractmethod
    def parse(script_path: str, *args) -> JsonObject:
        pass


class ScriptParser(Parser):

    @staticmethod
    def parse(script_path: str, *args) -> JsonObject:
        logger.info('Use Script Parser')

        try:
            with open(script_path, 'r', encoding='utf8') as f:
                content: Dict = json5.load(f)
        except Exception as e:
            # logger.warning(e)
            try:
                with open(script_path, 'r', encoding='big5hkscs') as f:
                    content: Dict = json5.load(f)
            except Exception as e:
                logger.error(e)
                logger.error('無法解析指令碼，請檢查是否存在語法問題')
                return None

        logger.debug('Script content')
        logger.debug(content)

        objects: List[Dict[str, Any]] = content['scripts']

        label_maps: Dict[str, JsonObject] = {}
        pending_dict: Dict[JsonObject, str] = {}  # 如果對像要跳轉到未收入的label，則暫存該對像等待遍歷完成後(labelmaps完全更新)再新增內容

        try:
            head_object = ScriptParser.link_objects(objects, None, label_maps, pending_dict)
            if len(pending_dict) > 0:
                for json_object, target_label in pending_dict.items():
                    target_object = label_maps.get(target_label, None)
                    if target_object:
                        json_object.next_object = target_object
                    else:
                        logger.error(f'Could not find label {target_label}')
            return head_object
        except Exception as e:
            logger.error(e)
            logger.error('無法解析指令碼，請檢查是否存在語法問題')
            return None

    @staticmethod
    @logger.catch
    def link_objects(objects: List[Dict[str, Any]], target_object: JsonObject,
                     label_maps: Dict[str, JsonObject], pending_dict: Dict[JsonObject, str]) -> JsonObject:
        # 倒序遍歷指令碼，建立流程圖
        objects.reverse()
        current_object: JsonObject = None
        for content in objects:
            content: Dict
            current_object = JsonObject(content)
            # 新增label對映
            if content.get('label', None) is not None:
                if label_maps.get(content['label'], None) is not None:
                    logger.warning(f'Overwrite label {content["label"]} to object {content}')
                label_maps[content['label']] = current_object

            object_type = content.get('type', None)
            if object_type in ['event', 'subroutine', 'custom']:
                # 直接連線
                current_object.next_object = target_object
            elif object_type == 'sequence':
                current_object.next_object = target_object
                current_object.content['events'] = \
                    ScriptParser.link_objects(content['events'], None, label_maps, pending_dict)
            elif object_type == 'if':
                # 涉及兩個子序列的連線
                current_object.next_object = \
                    ScriptParser.link_objects(content['do'], target_object, label_maps, pending_dict)
                current_object.next_object_if_false = \
                    ScriptParser.link_objects(content['else'], target_object, label_maps, pending_dict)
            elif object_type == 'goto':
                if label_maps.get(content['tolabel'], None):
                    current_object.next_object = label_maps[content['tolabel']]
                else:
                    pending_dict[current_object] = content['tolabel']
            else:
                raise RuntimeError(f'Unexpected event type at {content}')
            target_object = current_object
        return current_object


class LegacyParser(Parser):

    @staticmethod
    def parse(script_path: str, *args) -> JsonObject:
        logger.info('Use Legacy Parser')

        try:
            with open(script_path, 'r', encoding='utf8') as f:
                content = json5.load(f)
        except Exception as e:
            # logger.warning(e)
            try:
                with open(script_path, 'r', encoding='big5hkscs') as f:
                    content = json5.load(f)
            except Exception as e:
                logger.error(e)
                logger.error('無法解析指令碼，請檢查是否存在語法問題')
                return None

        logger.debug('Script content')
        logger.debug(content)
        # 舊版指令碼無流程控制，只需倒序遍歷即可確定圖
        content.reverse()
        target_object = None
        current_object = None
        for v in content:
            current_object = JsonObject({
                'delay': v[0],
                'event_type': v[1].upper(),
                'message': v[2].lower(),
                'action': v[3],
                'type': 'event'
            })
            current_object.next_object = target_object
            target_object = current_object
        return current_object
