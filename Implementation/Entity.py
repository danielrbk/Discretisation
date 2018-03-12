from typing import Dict, List, Set, Tuple

from Implementation.TimeStamp import TimeStamp


class Entity(object):
    property_to_entities: Dict[int, Set['Entity']] = {}
    class_to_entities: Dict[int, Set['Entity']] = {}
    property_to_timestamps: Dict[int, List[TimeStamp]] = {}

    def __init__(self, entity_id: int, class_separator: int = None):
        self.entity_id: int = entity_id
        self.properties: Dict[int, List[TimeStamp]] = {}
        self.class_separator: int = class_separator

    @staticmethod
    def pair_property_entity(entity: 'Entity', temporal_property: int) -> None:
        if temporal_property not in Entity.property_to_entities:
            Entity.property_to_entities[temporal_property] = set()
        Entity.property_to_entities[temporal_property].add(entity)

    @staticmethod
    def get_entities_for_property(temporal_property: int) -> Set['Entity']:
        return Entity.property_to_entities[temporal_property]

    @staticmethod
    def pair_class_entity(entity: 'Entity', class_id: int) -> None:
        if class_id not in Entity.class_to_entities:
            Entity.class_to_entities[class_id] = set()
        Entity.class_to_entities[class_id].add(entity)

    @staticmethod
    def get_entities_for_class(class_id) -> Set['Entity']:
        return Entity.class_to_entities[class_id]

    @staticmethod
    def pair_property_timestamp(property_id: int, time_stamp: TimeStamp) -> None:
        if property_id not in Entity.property_to_timestamps:
            Entity.property_to_timestamps[property_id] = []
        Entity.property_to_timestamps[property_id].append(time_stamp)

    @staticmethod
    def get_timestamp_for_property(property_id) -> List[TimeStamp]:
        return Entity.property_to_timestamps[property_id]

    def get_entity_id(self) -> int:
            return self.entity_id

    def add_time_stamp(self, property_id: int, time_stamp: TimeStamp):
        if self.class_separator is not None and self.class_separator == property_id:
            class_id = int(time_stamp.value)
            Entity.pair_class_entity(self, class_id)
        else:
            if property_id not in self.properties:
                self.properties[property_id] = []
            self.properties[property_id].append(time_stamp)
            Entity.pair_property_entity(self, property_id)
            Entity.pair_property_timestamp(property_id, time_stamp)

    def get_properties(self) -> Dict[int, List[TimeStamp]]:
        return self.properties

    def __hash__(self):
        return self.entity_id.__hash__()

    def __str__(self):
        ss = self.entity_id.__str__() + ":\n "
        strs = []
        for key in self.properties.keys():
            s = "[%s: [" % key
            vals = []
            for val in self.properties[key]:
                vals.append(val.__str__())
            s += ", ".join(vals) + "]"
            strs.append(s)
        return ss + "\n".join(strs)

    @staticmethod
    def get_maps() -> Tuple[Dict[int, Set['Entity']],Dict[int, Set['Entity']],Dict[int, List[TimeStamp]]]:
        return Entity.property_to_entities, Entity.class_to_entities, Entity.property_to_timestamps

