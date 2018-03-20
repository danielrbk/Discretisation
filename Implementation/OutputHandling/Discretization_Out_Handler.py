import pandas as pd
import Implementation.AbstractDiscretisation as ad
def convert_cutpoints_to_output(property_to_entities, class_to_entities, property_to_timestamps, cutpoints):
    cutpoints_dict = {}
    cutpoints_df = pd.DataFrame()
