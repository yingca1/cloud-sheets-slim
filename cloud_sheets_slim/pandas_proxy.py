import pandas as pd


class PandasProxy:
    def __init__(self, all_records):
        self.source_df = pd.DataFrame(all_records)

    def _get_header(self):
        return self.source_df.columns.tolist()

    def _get_values(self):
        return self.source_df.values.tolist()

    def get_df(self):
        return self.source_df

    def find_one(self, query):
        df = self.source_df.copy()

        for key, value in query.items():
            df = df[self.source_df[key] == value]

        result = (
            df.head(1).to_dict("records")[0]
            if not df.empty
            else None
        )

        if result is None:
            return None

        result = {k: v for k, v in result.items() if v != ""}
        return result

    def find(self, query={}):
        df = self.source_df.copy()
        
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle MongoDB-style operators
                for op, val in value.items():
                    if op == "$gt":
                        df = df[df[key] > val]
                    elif op == "$gte":
                        df = df[df[key] >= val]
                    elif op == "$lt":
                        df = df[df[key] < val]
                    elif op == "$lte":
                        df = df[df[key] <= val]
                    elif op == "$ne":
                        df = df[df[key] != val]
                    elif op == "$in":
                        df = df[df[key].isin(val)]
            else:
                # Handle simple equality
                df = df[df[key] == value]

        result = df.to_dict("records") if not df.empty else []
        result = [{k: v for k, v in res.items() if v != ""} for res in result]
        
        return result

    def insert_one(self, record):
        self.source_df = pd.concat([self.source_df, pd.DataFrame([record])], ignore_index=True).fillna('')

    def insert_many(self, records):
        self.source_df = pd.concat([self.source_df, pd.DataFrame(records)], ignore_index=True).fillna('')

    def replace_one(self, query, new_record):
        mask = (self.source_df[list(query.keys())] == pd.Series(query)).all(axis=1)
        idx = self.source_df[mask].index

        if not idx.empty:
            new_record_copy = new_record.copy()

            for col in self.source_df.columns:
                if col not in new_record_copy:
                    new_record_copy[col] = self.source_df.at[idx[0], col]

            for col in new_record:
                if col not in self.source_df.columns:
                    self.source_df[col] = pd.NA

            self.source_df.loc[idx[0]] = new_record_copy

    def update_one(self, query, new_items, upsert=False):
        query_mask = self.source_df.apply(
            lambda row: all(row[k] == v for k, v in query.items()), axis=1
        )

        if query_mask.any():
            row_idx = self.source_df.index[query_mask][0]

            for key, value in new_items.items():
                if key not in self.source_df.columns:
                    self.source_df[key] = None
                self.source_df.at[row_idx, key] = value
        elif upsert:
            new_row = {**query, **new_items}
            self.insert_one(new_row)

    def update_many(self, query, update, upsert=False):
        if self.source_df.empty and upsert:
            self.insert_one({**query, **update})
            return

        if not set(query.keys()).issubset(self.source_df.columns):
            raise KeyError("Some query keys are not in the DataFrame")

        mask = (self.source_df[list(query.keys())] == pd.Series(query)).all(axis=1)
        matching_rows = self.source_df[mask]

        if not matching_rows.empty:
            self.source_df.update(matching_rows.assign(**update))

        if upsert and matching_rows.empty:
            new_row = {**query, **update}
            self.source_df = self.source_df.append(new_row, ignore_index=True)

    def delete_one(self, query):
        for key, value in query.items():
            self.source_df = self.source_df[self.source_df[key] != value]

    def delete_many(self, query):
        """
        Delete multiple records that match the query criteria.
        Supports basic MongoDB-style queries including $in operator.
        """
        if len(query) == 1 and isinstance(query[list(query.keys())[0]], dict):
            # Handle MongoDB-style operators
            field = list(query.keys())[0]
            operator_dict = query[field]
            
            if "$in" in operator_dict:
                # Handle $in operator
                values = operator_dict["$in"]
                mask = self.source_df[field].isin(values)
                self.source_df = self.source_df[~mask]
            else:
                raise ValueError(f"Unsupported operator in query: {operator_dict}")
        else:
            # Handle simple equality queries
            mask = (self.source_df[list(query.keys())] == pd.Series(query)).all(axis=1)
            self.source_df = self.source_df[~mask]

    def count_records(self, query={}):
        if query:
            mask = (self.source_df[list(query.keys())] == pd.Series(query)).all(axis=1)
            return len(self.source_df[mask])
        else:
            return len(self.source_df)
