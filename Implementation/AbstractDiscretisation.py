import itertools
from abc import ABC, abstractmethod
from functools import reduce
from multiprocessing.pool import ThreadPool
from os.path import exists

import numpy as np

from Implementation.BinInterval import BinInterval
from typing import Dict, List, Set, Tuple

from Implementation.Constants import THREAD_COUNT, CLASS_SEPARATOR, debug_print
from Implementation.DataRow import DataRow
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp
from Tests.Constants import deep_getsizeof


class Discretization(ABC):
    bin_id = 0

    def __init__(self, interval_max_gap, window_size):
        self.max_gap: int = int(interval_max_gap)
        self.property_to_ranges: Dict[int, List[BinInterval]] = {}  # List of bin cutpoints, using OOP
        self.bin_count: int = 0  # Number of bins
        self.bin_symbol: int = -1  # Discretization symbol
        self.bins_cutpoints: Dict[int, List[float]] = {}  # List of bin cutpoints
        self.property_folder = ""
        self.window_size = int(window_size)

    def transform(self, property_id: int, val: TimeStamp) -> None:
        """
        Given a time stamp, discretize its value according to the precalculated bin cutpoints.
        :param property_id: Property id of the time stamp
        :param val: Time stamp to discretize
        :return: None
        """
        try:
            while not self.property_to_ranges[property_id][self.bin_id].discretize(val):
                self.bin_id += 1
        except:
            print(val)
            raise


    @abstractmethod
    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]) -> Dict[int, List[float]]:
        """
        Calculate bin cutpoints according to the discretization method.
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Dictionary mapping each property id to the list of generated cutpoints
        """
        pass

    @abstractmethod
    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> List[float]:
        """
        Calculate bin cutpoints according to the discretization method for a certain property.
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :param property_id: The certain property to discretize
        :return: List of cutpoints generated for the property.
        """
        pass

    @abstractmethod
    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str) -> None:
        """
        Write any auxiliary information to the path that may interest the client, such as scores used in the discretisation etc...
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :param path: Path to the auxiliary information file
        :return: None
        """
        pass

    @abstractmethod
    def get_discretization_name(self) -> str:
        """
        Get a discretisation name characterizing the discretization performed, name should include the parameters used by the discretization.
        :return: Discretization name
        """
        pass

    def parallel_cutpoint_set(self, property_to_entities: Dict[int, Set[Entity]],
                              class_to_entities: Dict[int, Set[Entity]],
                              property_to_timestamps: Dict[int, List[TimeStamp]]) -> Dict[int, List[float]]:
        """
        Wrapper method, implementing multithreaded approach to discretize every property simultaneously
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Dictionary mapping each property id to the list of generated cutpoints
        """
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

    def set_bin_ranges_from_cutpoints_for_property(self, property_id) -> None:
        """
        Induces the OOP version of bin cutpoints on the discretization object, by using the class BinInterval
        :return: None
        """
        self.bin_symbol = -1
        bin_cutpoints = self.bins_cutpoints[property_id]
        if len(bin_cutpoints) != 0:
            bin_ranges = [BinInterval(property_id, self.get_symbol(), float('-inf'), bin_cutpoints[0])]
            for i in range(1, len(bin_cutpoints)):
                bin_ranges.append(BinInterval(property_id, self.get_symbol(), bin_cutpoints[i - 1], bin_cutpoints[i]))
            bin_ranges.append(BinInterval(property_id, self.get_symbol(), bin_cutpoints[-1], float('inf')))
            self.property_to_ranges[property_id] = bin_ranges

    def set_bin_ranges_from_cutpoints(self):
        for property_id in self.bins_cutpoints:
            self.set_bin_ranges_from_cutpoints_for_property(property_id)

    def get_symbol(self) -> int:
        """
        Get discretizaiton symbol and increment
        :return: Int representing the symbol of the bin.
        """
        self.bin_symbol += 1
        return self.bin_symbol

    def discretize(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        """
        Discretize the input dataset, represented as 3 dictionaries enabling access to the data, and return a
        discretized copy of these dictionaries. The original maps remain unchanged.
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Discretized *copies* of the input dictionaries.
        """
        property_to_entities, class_to_entities, property_to_timestamps = self.get_copy_of_maps(property_to_entities,
                                                                                                class_to_entities,
                                                                                                property_to_timestamps)
        cutpoints = self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)
        self.bins_cutpoints = cutpoints
        self.set_bin_ranges_from_cutpoints()

        self.abstract(property_to_entities,class_to_entities,property_to_timestamps)
        return property_to_entities, class_to_entities, property_to_timestamps

    def discretize_property(self, property_to_entities: Dict[int, Set[Entity]],
                            class_to_entities: Dict[int, Set[Entity]],
                            property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        if not property_to_entities and not class_to_entities and not property_to_timestamps:
            if self.get_map_used() == "property_to_entities":
                self.load_property_to_entity(property_to_entities, property_id)
            elif self.get_map_used() == "class_to_entities":
                self.load_class_to_entity(class_to_entities, property_id)
            elif self.get_map_used() == "property_to_timestamps":
                self.load_property_to_timestamps(property_to_timestamps, property_id)

        if property_to_timestamps:
            property_to_timestamps = self.paa_p2t(property_to_timestamps)
        elif property_to_entities:
            property_to_entities = self.paa_p2e(property_to_entities)
        else:
            class_to_entities = self.paa_c2e(class_to_entities)

        self.bins_cutpoints[property_id] = self.set_bin_ranges_for_property(property_to_entities, class_to_entities,
                                                                            property_to_timestamps, property_id)

        if len(self.bins_cutpoints[property_id]) != 0:
            self.set_bin_ranges_from_cutpoints_for_property(property_id)
            self.abstract_property(property_to_entities,class_to_entities,property_to_timestamps,property_id)
            return property_to_entities,class_to_entities,property_to_timestamps

        return {}, {}, {}

    def discretize_property_without_abstracting(self, property_to_entities: Dict[int, Set[Entity]],
                            class_to_entities: Dict[int, Set[Entity]],
                            property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        self.bins_cutpoints[property_id] = self.set_bin_ranges_for_property(property_to_entities, class_to_entities,
                                                                            property_to_timestamps, property_id)

    def abstract(self,  property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]]):
        for property_id in property_to_timestamps.keys():
            if property_id not in self.property_to_ranges:
                continue
            l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
            i = 0
            for val in l:
                self.transform(property_id, val)
                i += 1
            self.bin_id = 0
            if self.max_gap >= 0:
                property_to_timestamps[property_id] = []
                entities = property_to_entities[property_id]
                for entity in entities:
                    time_stamps: List[TimeStamp] = entity.properties[property_id]
                    sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value,ts.start_point))
                    ts_index = 0
                    new_timestamps = []
                    prev_ts = None
                    curr_val = -100
                    # connect time stamps
                    while ts_index < len(sorted_time_stamps):
                        curr_ts = sorted_time_stamps[ts_index]
                        if curr_val != curr_ts.value:
                            if prev_ts is not None:
                                new_timestamps.append(prev_ts)
                            prev_ts = curr_ts
                            curr_val = curr_ts.value
                        else:
                            if curr_ts.start_point - prev_ts.end_point - 1 <= self.max_gap:
                                prev_ts.end_point = curr_ts.end_point
                            else:
                                new_timestamps.append(prev_ts)
                                prev_ts = curr_ts
                        if ts_index + 1 == len(sorted_time_stamps):
                            new_timestamps.append(prev_ts)
                        ts_index += 1
                    entity.properties[property_id] = new_timestamps
                    property_to_timestamps[property_id] += new_timestamps
                property_to_timestamps[property_id] = sorted(property_to_timestamps[property_id], key=lambda ts: ts.start_point)

    def paa_p2t(self, property_to_timestamps):
        """
        Performs Piecewise Aggregate Approximation on a given values, reducing
        the dimension of the values length n to w approximations.
        each value from the approximations is the mean of frame size values.
        returns the reduced dimension data set, as well as the indices corresponding to the original
        data for each reduced dimension.
        """
        new_property_to_timestamps = {}
        for property_id in property_to_timestamps:
            new_property_to_timestamps[property_id] = []
            entities: Dict[int, List[TimeStamp]] = {}
            for ts in property_to_timestamps[property_id]:
                e = ts.entity_id
                if e not in entities:
                    entities[e] = [ts]
                else:
                    entities[e].append(ts)

            lists = [self.paa_timestamps(entities[e]) for e in entities]
            new_property_to_timestamps[property_id] = list(itertools.chain.from_iterable(lists))

            new_property_to_timestamps[property_id] = list(sorted(new_property_to_timestamps[property_id],key=lambda ts: ts.start_point))
        return new_property_to_timestamps

    def paa_p2e(self, property_to_entities: Dict[int,Set[Entity]]):
        """
        Performs Piecewise Aggregate Approximation on a given values, reducing
        the dimension of the values length n to w approximations.
        each value from the approximations is the mean of frame size values.
        returns the reduced dimension data set, as well as the indices corresponding to the original
        data for each reduced dimension.
        """
        new_property_to_entity = {}
        entities = {}
        for property_id in property_to_entities:
            new_property_to_entity[property_id] = set()
            for e in property_to_entities[property_id]:
                if e.entity_id not in entities:
                    new_e = Entity(e.entity_id,e.entity_class)
                    for property_id in e.properties:
                        new_e.properties[property_id] = self.paa_timestamps(e.properties[property_id])
                    entities[e.entity_id] = new_e
                else:
                    new_e = entities[e.entity_id]
                new_property_to_entity[property_id].add(new_e)

        return new_property_to_entity

    def paa_c2e(self, class_to_entities: Dict[int, Set[Entity]]):
        """
        Performs Piecewise Aggregate Approximation on a given values, reducing
        the dimension of the values length n to w approximations.
        each value from the approximations is the mean of frame size values.
        returns the reduced dimension data set, as well as the indices corresponding to the original
        data for each reduced dimension.
        """

        new_class_to_entity = {}
        for c in class_to_entities:
            new_class_to_entity[c] = set()
            for e in class_to_entities[c]:
                new_e = Entity(e.entity_id, e.entity_class)
                for property_id in e.properties:
                    new_e.properties[property_id] = self.paa_timestamps(e.properties[property_id])
                new_class_to_entity[c].add(new_e)

        return new_class_to_entity

    def paa_timestamps(self,timestamps: List[TimeStamp]):
        if self.window_size == 1:
            return [TimeStamp(ts.value, ts.start_point, ts.end_point, ts.entity_id, ts.ts_class) for ts in timestamps]
        timestamps = sorted(timestamps, key=lambda ts: ts.start_point)
        start_point = timestamps[0].start_point
        end_point = timestamps[-1].start_point
        time_point = start_point
        i = 0
        new_values = []
        while time_point < end_point:
            count = 0
            s = 0
            while i < len(timestamps) and timestamps[i].start_point < time_point + self.window_size:
                s += timestamps[i].value
                count += 1
                i += 1
            if count != 0:
                val = s / count
                new_values.append(TimeStamp(val, time_point, time_point+self.window_size, timestamps[i-1].entity_id,timestamps[i-1].ts_class))
            time_point += self.window_size
        '''
        values = [ts.value for ts in timestamps]

        values_length = len(values)

        frame_size = self.window_size

   

        frame_start = 0

        approximation = []

        indices_ranges = []

        loop_limit = values_length - frame_size

        while frame_start <= loop_limit:
            to = int(frame_start + frame_size)
            indices_ranges.append((frame_start, to))
            new_values.append(TimeStamp(np.mean(np.array(values[frame_start: to])),
                                        timestamps[frame_start].start_point,
                                        timestamps[to-1].end_point,timestamps[frame_start].entity_id,
                                        timestamps[frame_start].ts_class))
            frame_start += frame_size

        # handle the remainder if n % w != 0
        if frame_start < values_length:
            indices_ranges.append((frame_start, values_length))
            new_values.append(TimeStamp(np.mean(np.array(values[frame_start: values_length])),
                                        timestamps[frame_start].start_point,
                                        timestamps[values_length-1].end_point, timestamps[frame_start].entity_id,
                                        timestamps[frame_start].ts_class))
        '''

        return new_values

    def abstract_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        if property_to_timestamps:
            l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
            i = 0
            for val in l:
                self.transform(property_id, val)
                i += 1
            self.bin_id = 0
            self.abstract_property_in_property_to_timestamps(property_to_timestamps,property_id)
        elif property_to_entities:
            self.abstract_property_in_property_to_entities(property_to_entities, property_id)
        else:
            self.abstract_property_in_class_to_entities(class_to_entities,property_id)

    def abstract_property_in_property_to_timestamps(self, property_to_timestamps: Dict[int, List[TimeStamp]], property_id):
        if self.max_gap >= 0:
            updated_list = []
            entities: Dict[int, List[TimeStamp]] = {}
            for ts in property_to_timestamps[property_id]:
                e = ts.entity_id
                if e not in entities:
                    entities[e] = [ts]
                else:
                    entities[e].append(ts)
            for e in entities:
                time_stamps = entities[e]
                sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value,ts.start_point))
                ts_index = 0
                new_timestamps = []
                prev_ts = None
                curr_val = float('-inf')
                # connect time stamps
                while ts_index < len(sorted_time_stamps):
                    curr_ts = sorted_time_stamps[ts_index]
                    if curr_val != curr_ts.value:
                        if prev_ts is not None:
                            new_timestamps.append(prev_ts)
                        prev_ts = curr_ts
                        curr_val = curr_ts.value
                    else:
                        if curr_ts.start_point - prev_ts.end_point - 1 <= self.max_gap:
                            prev_ts.end_point = curr_ts.end_point
                        else:
                            new_timestamps.append(prev_ts)
                            prev_ts = curr_ts
                    if ts_index + 1 == len(sorted_time_stamps):
                        new_timestamps.append(prev_ts)
                    ts_index += 1
                updated_list += new_timestamps
            property_to_timestamps[property_id] = sorted(updated_list, key=lambda ts: ts.start_point)

    def abstract_property_in_property_to_entities(self, property_to_entities: Dict[int, Set[Entity]], property_id):
        property_to_timestamps: Dict[int, List[TimeStamp]] = {property_id: []}
        for e in property_to_entities[property_id]:
            property_to_timestamps[property_id] += e.properties[property_id]
        l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
        i = 0

        for val in l:
            self.transform(property_id, val)
            i += 1
        self.bin_id = 0
        if self.max_gap >= 0:
            property_to_timestamps[property_id] = []
            entities = property_to_entities[property_id]
            for entity in entities:
                time_stamps: List[TimeStamp] = entity.properties[property_id]
                sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value, ts.start_point))
                ts_index = 0
                new_timestamps = []
                prev_ts = None
                curr_val = float('-inf')
                # connect time stamps
                while ts_index < len(sorted_time_stamps):
                    curr_ts = sorted_time_stamps[ts_index]
                    if curr_val != curr_ts.value:
                        if prev_ts is not None:
                            new_timestamps.append(prev_ts)
                        prev_ts = curr_ts
                        curr_val = curr_ts.value
                    else:
                        if curr_ts.start_point - prev_ts.end_point - 1 <= self.max_gap:
                            prev_ts.end_point = curr_ts.end_point
                        else:
                            new_timestamps.append(prev_ts)
                            prev_ts = curr_ts
                    if ts_index + 1 == len(sorted_time_stamps):
                        new_timestamps.append(prev_ts)
                    ts_index += 1
                entity.properties[property_id] = new_timestamps
                property_to_timestamps[property_id] += new_timestamps
            property_to_timestamps[property_id] = sorted(property_to_timestamps[property_id],
                                                         key=lambda ts: ts.start_point)

    def abstract_property_in_class_to_entities(self, class_to_entities: Dict[int, Set[Entity]], property_id):
        property_to_entities = {property_id: set()}
        for c in class_to_entities:
            property_to_entities[property_id] = property_to_entities[property_id].union(class_to_entities[c])
        self.abstract_property_in_property_to_entities(property_to_entities, property_id)

    def set_and_get_cutpoints(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]]) -> None:
        """
        Calculates the discretization cutpoints without performing the actual discretization.
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Nones
        """
        cutpoints = self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)
        self.bins_cutpoints = cutpoints

    def confine_view_to_property(self, key_property: int, property_to_entities: Dict[int, Set[Entity]],
                                 class_to_entities: Dict[int, Set[Entity]],
                                 property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        """
        Return copies of the input dictionaries in which only entries relevant to the key property remain.
        :param key_property: Property for which we confine the view
        :param property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Copes of the input dictionaries, with only the key property appearing in the dictionaries.
        """
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

    def load_property_to_entity(self, property_to_entities: Dict[int, Set['Entity']], property_id: int) -> Dict[int, Set['Entity']]:
        property_to_entities[property_id] = set()
        entities: Dict[int, Entity] = {}
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, 0, CLASS_SEPARATOR)
                    property_to_entities[property_id].add(e)
                    entities[eid] = e
                    e.properties[property_id] = []
                e.properties[property_id].append(dr.get_time_stamp())
        if exists((self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR)):
            with open(self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR) as f:
                for line in f:
                    dr = DataRow.get_data_from_row(line)
                    eid = dr.get_entity_id()
                    if eid in entities:
                        e = entities[eid]
                        c = int(dr.get_time_stamp().value)
                        e.entity_class = c
                        for pid in e.properties:
                            for ts in e.properties[pid]:
                                ts.ts_class = c
        return property_to_entities

    def load_class_to_entity(self, class_to_entities: Dict[int, Set['Entity']], property_id: int) -> Dict[int, Set['Entity']]:
        entities: Dict[int, Entity] = {}
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, 0, CLASS_SEPARATOR)
                    entities[eid] = e
                    e.properties[property_id] = []
                e.properties[property_id].append(dr.get_time_stamp())
        if exists((self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR)):
            with open(self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR) as f:
                for line in f:
                    dr = DataRow.get_data_from_row(line)
                    eid = dr.get_entity_id()
                    if eid in entities:
                        e = entities[eid]
                        c = int(dr.get_time_stamp().value)
                        e.entity_class = c
                        if c not in class_to_entities:
                            class_to_entities[c] = set()
                        class_to_entities[c].add(e)
                        for pid in e.properties:
                            for ts in e.properties[pid]:
                                ts.ts_class = c
        return class_to_entities

    def load_property_to_timestamps(self,  property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> Dict[int, List[TimeStamp]]:
        property_to_timestamps[property_id] = []
        entity_to_timestamps: Dict[int,List[TimeStamp]] = {}
        entity_count = 0
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entity_to_timestamps:
                    entity_to_timestamps[eid].append(dr.get_time_stamp())
                else:
                    entity_count += 1
                    if entity_count % 10000 == 0:
                        print("Total entities read: %s" % entity_count)
                        #debug_print("Memory used by map: %s" % (deep_getsizeof(entity_to_timestamps,set()) / (1024*1024)))
                    entity_to_timestamps[eid] = [dr.get_time_stamp()]
                del dr
        if exists((self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR)):
            with open(self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR) as f:
                for line in f:
                    dr = DataRow.get_data_from_row(line)
                    eid = dr.get_entity_id()
                    c = int(dr.get_time_stamp().value)
                    if eid in entity_to_timestamps:
                        for ts in entity_to_timestamps[eid]:
                            ts.ts_class = c
        combined_list = []
        count = 0
        lists = len(entity_to_timestamps.values())
        combined_list = list(itertools.chain.from_iterable(entity_to_timestamps.values()))
        property_to_timestamps[property_id] = combined_list
        return property_to_timestamps

    @staticmethod
    def get_copy_of_maps(old_property_to_entities: Dict[int, Set[Entity]],
                         old_class_to_entities: Dict[int, Set[Entity]],
                         old_property_to_timestamps: Dict[int, List[TimeStamp]]) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        """
        Returns deep copies of the input dictionaries
        :param old_property_to_entities: A dictionary mapping property ids to the set of entities containing the property
        :param old_class_to_entities: A dictionary mapping class ids to the set of entities under this class
        :param old_property_to_timestamps: A dictionary mapping property ids to the list of timestamps belonging to that property.
        :return: Deep copies of these dictionaries.
        """
        property_to_entities: Dict[int, Set['Entity']] = {}
        class_to_entities: Dict[int, Set['Entity']] = {}
        property_to_timestamps: Dict[int, List[TimeStamp]] = {}
        old_timestamp_to_new: Dict[Tuple, TimeStamp] = {ts: TimeStamp.deep_copy(ts) for time_stamps in
                                                            old_property_to_timestamps.values() for ts in
                                                            time_stamps}
        property_to_timestamps = {property_id: [old_timestamp_to_new[ts] for ts in
                                                old_property_to_timestamps[property_id]] for property_id in
                                  old_property_to_timestamps.keys()}

        for class_id in old_class_to_entities.keys():
            class_to_entities[class_id] = set()
            for entity in old_class_to_entities[class_id]:
                properties = entity.properties.copy()
                e = Entity(entity.entity_id, class_id, entity.class_separator)

                properties = {key: [old_timestamp_to_new[ts] for ts in properties[key]] for key in properties.keys()}
                property_ids = properties.keys()
                diff = set(property_ids).difference(property_to_entities.keys())
                property_to_entities.update({p_id: set() for p_id in diff})
                for key in property_ids:
                    property_to_entities[key].add(e)
                e.properties = properties
                class_to_entities[class_id].add(e)

        return property_to_entities, class_to_entities, property_to_timestamps

    @staticmethod
    def get_copy_of_property_to_timestamps(old_property_to_timestamps: Dict[int,List[TimeStamp]]):
        property_to_timestamps = {property_id: [ts.deep_copy() for ts in
                                                old_property_to_timestamps[property_id]] for property_id in
                                  old_property_to_timestamps.keys()}
        return property_to_timestamps

    @staticmethod
    def get_copy_of_property_to_entities(old_property_to_entities: Dict[int, Set[Entity]]):
        property_to_entities: Dict[int, Set[Entity]] = {property_id: set([e.deep_copy() for e
                                                                          in old_property_to_entities[property_id]])
                                                        for property_id in old_property_to_entities}
        return property_to_entities

    @staticmethod
    def get_copy_of_class_to_entities(old_class_to_entities: Dict[int, Set[Entity]]):
        class_to_entities: Dict[int, Set[Entity]] = {c: set([e.deep_copy() for e
                                                                          in old_class_to_entities[c]])
                                                        for c in old_class_to_entities}
        return class_to_entities

    @staticmethod
    def property_to_timestamps_to_class_to_entities(property_to_timestamps: Dict[int, List[TimeStamp]]):
        class_to_entities: Dict[int,Set[Entity]] = {}
        entities: Dict[int, Entity] = {}
        for property_id in property_to_timestamps:
            for ts in property_to_timestamps[property_id]:
                e_id = ts.entity_id
                if e_id in entities:
                    e = entities[e_id]
                else:
                    c = ts.ts_class
                    if c not in class_to_entities:
                        class_to_entities[c] = set()
                    e = Entity(e_id,c,-1)
                    entities[e_id] = e
                    class_to_entities[c].add(e)
                if property_id not in e.properties:
                    e.properties[property_id] = []
                e.properties[property_id].append(ts)
        return class_to_entities

    @staticmethod
    def property_to_timestamps_to_property_to_entity(property_to_timestamps: Dict[int, List[TimeStamp]]):
        property_to_entity: Dict[int, Set[Entity]] = {}
        entities: Dict[int, Entity] = {}
        for property_id in property_to_timestamps:
            property_to_entity[property_id] = set()
            for ts in property_to_timestamps[property_id]:
                e_id = ts.entity_id
                if e_id in entities:
                    e = entities[e_id]
                else:
                    c = ts.ts_class
                    e = Entity(e_id, c, -1)
                    entities[e_id] = e
                    property_to_entity[property_id].add(e)
                if property_id not in e.properties:
                    e.properties[property_id] = []
                e.properties[property_id].append(ts)
        return property_to_entity

    @staticmethod
    @abstractmethod
    def get_map_used():
        pass


