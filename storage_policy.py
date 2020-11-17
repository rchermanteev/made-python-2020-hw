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
        format_to_keys = ""
        format_to_values = ""
        keys = list(word_to_docs_mapping.keys())
        values = list(word_to_docs_mapping.values())
        for i in range(len(keys)):
            values[i] = " ".join(values[i])
            values[i] = values[i].encode()
            keys[i] = keys[i].encode()
            format_to_keys += f"{len(keys[i])}s"
            format_to_values += f"{len(values[i])}s"

        format_to_keys = format_to_keys.encode()
        format_to_values = format_to_values.encode()
        obj_format_to_keys = struct.pack(f"{len(format_to_keys)}s", format_to_keys)
        obj_format_to_values = struct.pack(f"{len(format_to_values)}s", format_to_values)
        obj_keys = struct.pack(format_to_keys, *keys)
        obj_values = struct.pack(format_to_values, *values)
        with open(filepath, "wb") as file:
            file.write(obj_format_to_keys)
            file.write("\n".encode())
            file.write(obj_format_to_values)
            file.write("\n".encode())
            file.write(obj_keys)
            file.write("\n".encode())
            file.write(obj_values)

    @staticmethod
    def load(filepath: str):
        with open(filepath, "rb") as file:
            obj_format_to_keys = file.readline().strip()
            obj_format_to_values = file.readline().strip()
            obj_keys = file.readline().strip()
            obj_values = file.readline().strip()

        format_to_keys = struct.unpack(f"{len(obj_format_to_keys)}s", obj_format_to_keys)[0].decode()
        format_to_values = struct.unpack(f"{len(obj_format_to_values)}s", obj_format_to_values)[0].decode()
        keys = [key.decode() for key in struct.unpack(format_to_keys, obj_keys)]
        values = [value.decode().split() for value in struct.unpack(format_to_values, obj_values)]

        return dict(zip(keys, values))
