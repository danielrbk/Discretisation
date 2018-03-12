from abc import ABC, abstractmethod
from multiprocessing.pool import ThreadPool

from Implementation.BinInterval import BinInterval
from typing import Dict, List, Set, Tuple

from Implementation.Constants import THREAD_COUNT
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Discretization(ABC):
    bin_id = 0

    def __init__(self):
        self.property_to_ranges: Dict[int, List[BinInterval]] = {}
        self.bin_count = 0
        self.bin_symbol = -1
        self.bins_cutpoints = {}

    def transform(self, property_id: int, val: TimeStamp):
        while not self.property_to_ranges[property_id][self.bin_id].discretize(val):
            self.bin_id += 1

    @abstractmethod
    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        pass

    @abstractmethod
    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        pass

    def parallel_cutpoint_set(self, property_to_entities: Dict[int, Set[Entity]],
                              class_to_entities: Dict[int, Set[Entity]],
                              property_to_timestamps: Dict[int, List[TimeStamp]]):
        def f(property_id):
            return self.set_bin_ranges_for_property(property_to_entities,class_to_entities,property_to_timestamps,property_id)

        property_ids = list(property_to_entities.keys())

        pool = ThreadPool(THREAD_COUNT)
        results = pool.map(f, property_ids)

        # close the pool and wait for the work to finish
        pool.close()
        pool.join()

        cutpoints = {property_ids[i]: results[i] for i in range(len(property_ids))}
        return cutpoints

    def set_bin_ranges_from_cutpoints(self):
        for property_id in self.bins_cutpoints.keys():
            self.bin_symbol = -1
            bin_cutpoints = self.bins_cutpoints[property_id]
            if len(bin_cutpoints) == 0:
                continue
            bin_ranges = [BinInterval(property_id, self.get_symbol(), float('-inf'), bin_cutpoints[0])]
            for i in range(1, len(bin_cutpoints)):
                bin_ranges.append(BinInterval(property_id, self.get_symbol(), bin_cutpoints[i - 1], bin_cutpoints[i]))
            bin_ranges.append(BinInterval(property_id, self.get_symbol(), bin_cutpoints[-1], float('inf')))
            self.property_to_ranges[property_id] = bin_ranges

    def get_symbol(self):
        self.bin_symbol += 1
        return self.bin_symbol

    def discretize(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        property_to_entities, class_to_entities, property_to_timestamps = self.get_copy_of_maps(property_to_entities,
                                                                                                class_to_entities,
                                                                                                property_to_timestamps)
        self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)
        self.set_bin_ranges_from_cutpoints()
        for property_id in property_to_timestamps.keys():
            if property_id not in self.property_to_ranges:
                continue
            l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
            for val in l:
                self.transform(property_id, val)
            self.bin_id = 0
        return property_to_entities, class_to_entities, property_to_timestamps

    def set_and_get_cutpoints(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]]) -> None:
        self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)

    def confine_view_to_property(self, key_property: int, property_to_entities: Dict[int, Set[Entity]],
                                 class_to_entities: Dict[int, Set[Entity]],
                                 property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        property_to_entities, class_to_entities, property_to_timestamps = self.get_copy_of_maps(property_to_entities,
                                                                                                class_to_entities,
                                                                                                property_to_timestamps)
        entities = property_to_entities[key_property]
        relevant_timestamps = property_to_timestamps[key_property]
        c2e = {c: class_to_entities[c].intersection(entities) for c in class_to_entities.keys()}

        def confine_view_in_entity(e):
            e.properties = {key_property: e.properties[key_property]}

        pool = ThreadPool(THREAD_COUNT)
        results = pool.map(confine_view_in_entity, entities)

        # close the pool and wait for the work to finish
        pool.close()
        pool.join()
        return {key_property: set(entities)}, c2e, {key_property: relevant_timestamps}

    @staticmethod
    def get_copy_of_maps(old_property_to_entities: Dict[int, Set[Entity]],
                         old_class_to_entities: Dict[int, Set[Entity]],
                         old_property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        property_to_entities: Dict[int, Set['Entity']] = {}
        class_to_entities: Dict[int, Set['Entity']] = {}
        property_to_timestamps: Dict[int, List[TimeStamp]] = {}
        old_timestamp_to_new: Dict[TimeStamp, TimeStamp] = {ts: TimeStamp(ts.value, ts.time) for time_stamps in
                                                            old_property_to_timestamps.values() for ts in
                                                            time_stamps}
        property_to_timestamps = {property_id: [old_timestamp_to_new[ts] for ts in
                                                old_property_to_timestamps[property_id]] for property_id in
                                  old_property_to_timestamps.keys()}

        for class_id in old_class_to_entities.keys():
            class_to_entities[class_id] = set()
            for entity in old_class_to_entities[class_id]:
                properties = entity.properties.copy()
                e = Entity(entity.entity_id, entity.class_separator)

                properties = {key: [old_timestamp_to_new[ts] for ts in properties[key]] for key in properties.keys()}
                property_ids = properties.keys()
                diff = set(property_ids).difference(property_to_entities.keys())
                property_to_entities.update({p_id: set() for p_id in diff})
                for key in property_ids:
                    property_to_entities[key].add(e)
                e.properties = properties
                class_to_entities[class_id].add(e)

        return property_to_entities, class_to_entities, property_to_timestamps
