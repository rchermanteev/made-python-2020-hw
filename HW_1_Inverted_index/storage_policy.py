import struct
import json


class StoragePolicy:
    @staticmethod
    def dump(word_to_docs_mapping, filepath: str):
        pass

    @staticmethod
    def load(filepath: str):
        pass


class JsonStoragePolicy(StoragePolicy):
    @staticmethod
    def dump(word_to_docs_mapping, filepath: str):
        with open(filepath, 'w') as outfile:
            json.dump(word_to_docs_mapping, outfile)

    @staticmethod
    def load(filepath: str):
        with open(filepath) as json_file:
            data = json.load(json_file)

        return data


class ArrayStoragePolicy(StoragePolicy):
    @staticmethod
    def dump(word_to_docs_mapping, filepath: str):
        keys = list(word_to_docs_mapping.keys())
        values = list(word_to_docs_mapping.values())
        format_str = ">1i"
        item_to_pack = [len(keys)]
        for i in range(len(keys)):
            key = keys[i].encode()
            # append key length
            format_str += "1B"
            item_to_pack.append(len(key))
            # append key
            format_str += f"{len(key)}s"
            item_to_pack.append(key)
            # append number values for key
            format_str += "1h"
            item_to_pack.append(len(values[i]))
            # append values for key
            for val in values[i]:
                format_str += "1h"
                item_to_pack.append(int(val))

        pack_pbj = struct.pack(format_str, *item_to_pack)
        with open(filepath, "wb") as file:
            file.write(pack_pbj)

    @staticmethod
    def load(filepath: str):
        keys = []
        values = []
        with open(filepath, "rb") as file:
            num_items = struct.unpack(">1i", file.read(4))[0]
            for _ in range(num_items):
                len_key = struct.unpack(">1B", file.read(1))[0]
                keys.append(struct.unpack(f">{len_key}s", file.read(len_key))[0].decode())
                num_vals = struct.unpack(">1h", file.read(2))[0]
                vals = list(struct.unpack(f">{num_vals}h", file.read(num_vals * 2)))
                values.append(list(map(str, vals)))

        return dict(zip(keys, values))
