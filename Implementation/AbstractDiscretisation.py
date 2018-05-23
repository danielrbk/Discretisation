from abc import ABC, abstractmethod
from multiprocessing.pool import ThreadPool

from Implementation.BinInterval import BinInterval
from typing import Dict, List, Set, Tuple

from Implementation.Constants import THREAD_COUNT, CLASS_SEPARATOR
from Implementation.DataRow import DataRow
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Discretization(ABC):
    bin_id = 0
    refresh_class_to_entity = False
    refresh_property_to_entity = False
    refresh_property_to_timestamps = False

    def __init__(self, interval_max_gap):
        self.max_gap: int = int(interval_max_gap)
        self.property_to_ranges: Dict[int, List[BinInterval]] = {}  # List of bin cutpoints, using OOP
        self.bin_count: int = 0  # Number of bins
        self.bin_symbol: int = -1  # Discretization symbol
        self.bins_cutpoints: Dict[int, List[float]] = {}  # List of bin cutpoints
        self.property_folder = ""

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

    def set_bin_ranges_from_cutpoints(self) -> None:
        """
        Induces the OOP version of bin cutpoints on the discretization object, by using the class BinInterval
        :return: None
        """
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
                    sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value,ts.time.start_point))
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
                            if curr_ts.time.start_point - prev_ts.time.end_point - 1 <= self.max_gap:
                                prev_ts.time.end_point = curr_ts.time.end_point
                            else:
                                new_timestamps.append(prev_ts)
                                prev_ts = curr_ts
                        if ts_index + 1 == len(sorted_time_stamps):
                            new_timestamps.append(prev_ts)
                        ts_index += 1
                    entity.properties[property_id] = new_timestamps
                    property_to_timestamps[property_id] += new_timestamps
                property_to_timestamps[property_id] = sorted(property_to_timestamps[property_id], key=lambda ts: ts.time.start_point)

    def abstract_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                   property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):

    def abstract_property_in_property_to_timestamps(self, property_to_timestamps: Dict[int, List[TimeStamp]], property_id):
        l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
        i = 0
        for val in l:
            self.transform(property_id, val)
            i += 1
        self.bin_id = 0
        if self.max_gap >= 0:
            property_to_timestamps[property_id] = []
            entities: Dict[int, List[TimeStamp]] = {}
            for ts in property_to_timestamps[property_id]:
                e = ts.entity_id
                if e not in entities:
                    entities[e] = [ts]
                else:
                    entities[e].append(ts)
            for time_stamps in entities:
                sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value,ts.time.start_point))
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
                        if curr_ts.time.start_point - prev_ts.time.end_point - 1 <= self.max_gap:
                            prev_ts.time.end_point = curr_ts.time.end_point
                        else:
                            new_timestamps.append(prev_ts)
                            prev_ts = curr_ts
                    if ts_index + 1 == len(sorted_time_stamps):
                        new_timestamps.append(prev_ts)
                    ts_index += 1
                property_to_timestamps[property_id] += new_timestamps
            property_to_timestamps[property_id] = sorted(property_to_timestamps[property_id], key=lambda ts: ts.time.start_point)

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
            entities: Dict[int, List[TimeStamp]] = {}
            for ts in property_to_timestamps[property_id]:
                e = ts.entity_id
                if e not in entities:
                    entities[e] = [ts]
                else:
                    entities[e].append(ts)
            for time_stamps in entities:
                sorted_time_stamps = sorted(time_stamps, key=lambda ts: (ts.value,ts.time.start_point))
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
                        if curr_ts.time.start_point - prev_ts.time.end_point - 1 <= self.max_gap:
                            prev_ts.time.end_point = curr_ts.time.end_point
                        else:
                            new_timestamps.append(prev_ts)
                            prev_ts = curr_ts
                    if ts_index + 1 == len(sorted_time_stamps):
                        new_timestamps.append(prev_ts)
                    ts_index += 1
                property_to_timestamps[property_id] += new_timestamps
            property_to_timestamps[property_id] = sorted(property_to_timestamps[property_id], key=lambda ts: ts.time.start_point)

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

    def load_property_to_entity(self, property_id: int, property_to_entities: Dict[int, Set['Entity']]) -> Dict[int, Set['Entity']]:
        property_to_entities[property_id] = set()
        entities: Dict[int, Entity] = {}
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, CLASS_SEPARATOR)
                    property_to_entities[property_id].add(e)
                    entities[eid] = e
                e.properties[property_id].append(dr.get_time_stamp())
        return property_to_entities

    def load_class_to_entity(self, property_id: int, class_to_entities: Dict[int, Set['Entity']]) -> Dict[int, Set['Entity']]:
        entities: Dict[int, Entity] = {}
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, CLASS_SEPARATOR)
                    class_to_entities[property_id].add(e)
                    entities[eid] = e
                e.properties[property_id].append(dr.get_time_stamp())
        with open(self.property_folder + "\\property%s.csv" % CLASS_SEPARATOR) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                    c = int(dr.get_time_stamp().value)
                    if c not in class_to_entities:
                        class_to_entities[c] = set()
                    class_to_entities[c].add(e)
        return class_to_entities

    def load_property_to_timestamps(self, property_id: int, property_to_timestamps: Dict[int, List[TimeStamp]]) -> Dict[int, List[TimeStamp]]:
        property_to_timestamps[property_id] = []
        with open(self.property_folder + "\\property%s.csv" % property_id) as f:
            for line in f:
                dr = DataRow.get_data_from_row(line)
                property_to_timestamps[property_id].append(dr.get_time_stamp())
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
        old_timestamp_to_new: Dict[Tuple, TimeStamp] = {ts: TimeStamp(ts.value, ts.time, ts.entity_id, ts.ts_class) for time_stamps in
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
