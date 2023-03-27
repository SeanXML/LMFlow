#!/usr/bin/env python
# coding=utf-8
"""This Python code defines a class Dataset with methods for initializing, loading,
and manipulating datasets from different backends such as Hugging Face and JSON.
 
The `Dataset` class includes methods for loading datasets from a dictionary and a Hugging
Face dataset, mapping datasets, and retrieving the backend dataset and arguments.
"""



# Importing necessary libraries and modules
import json
from pathlib import Path
from typing import Optional

from datasets import load_dataset
from datasets import Dataset as HFDataset

from lmflow.args import DatasetArguments


class Dataset:
    r"""
    Initializes the Dataset object with the given parameters.

    Parameters
    ------------
    data_args : DatasetArguments object.
        Contains the arguments required to load the dataset.

    backend : str,  default="huggingface"
        A string representing the dataset backend. Defaults to "huggingface".
    
    args : Optional.
        Positional arguments.
    
    kwargs : Optional.
        Keyword arguments.
    """
    def __init__(self, data_args=None, backend: str="huggingface", *args, **kwargs):
        self.data_args = data_args
        self.backend = backend
        self.backend_dataset = None
        self.type = None        # Original type of the dataset
        self.dataset_path = data_args.dataset_path

        if data_args.dataset_path is None:
            return

        if backend == "huggingface":
            data_files = [
                x.absolute().as_posix()
                 for x in Path(self.dataset_path).glob("*.json")
            ]

            # Iterate through all the files and ensure they have the same data type
            for single_file in data_files:
                with open(single_file) as fin:
                    json_data = json.load(fin)
                    if "type" not in json_data.keys():
                        raise ValueError(
                            '"type" field must be specified for data, e.g.'
                            '{\n'
                            '   "type": "text_only",\n'
                            '   "instances": [\n'
                            '       "Sentence 1: This is a sentence."\n'
                            '       "Sentence 2: This is another sentence."\n'
                            '   ]\n'
                            '}'
                        )

                    if self.type is None:
                        self.type = json_data["type"]
                    elif self.type != json_data["type"]:
                        raise ValueError(
                            'All task files must have same data types. Previous'
                            f' files have type "{self.type}", but in file'
                            f' {single_file}, it has type "{self.type}".'
                        )

            # Load the dataset using the HuggingFace dataset library
            extensions = "json"
            raw_dataset = load_dataset(
                extensions,
                data_files=data_files,
                field="instances",
                split="train",
                use_auth_token=None,
            )
            self.backend_dataset = raw_dataset
        elif backend == "json":
            # TODO (@Jiachun)
            pass
        else:
            raise NotImplementedError(f'Unsupported dataset backend "{backend}"')


    def _check_data_type(self):
        # TODO: check if data type and data structure matches, raise messages
        # with hints
        pass


    def from_dict(self, dict_obj: dict, *args, **kwargs):
        r"""
        Create a Dataset object from a dictionary.

        Parameters
        -----------

        dict_obj : dict.
            A dictionary containing the dataset information.
        
        args : Optional.
            Positional arguments.
        
        kwargs : Optional.
            Keyword arguments.

        Returns
        ---------

        self : Dataset object.
        """
        if self.backend == "huggingface":
            self.backend_dataset = HFDataset.from_dict(
                dict_obj["instances"], *args, **kwargs
            )
            self.type = dict_obj["type"]
            return self
        else:
            raise NotImplementedError(
                f'Currently .from_dict is not supported for backend "{backend}"'
            )



    def map(self, *args, **kwargs):
        r"""
        Parameters
        ------------
        args : Optional.
            Positional arguments.
        
        kwargs : Optional.
            Keyword arguments.

        Returns
        ---------

        self : Dataset object.
        """
        # If the dataset uses Hugging Face as the backend, 
        # call the `map()` function of the Hugging Face backend dataset
        if self.backend == "huggingface":
            # Set the mapped dataset as the backend dataset of the current dataset
            mapped_backend_dataset = self.backend_dataset.map(*args, **kwargs)
            self.backend_dataset = mapped_backend_dataset
            return self
        else:
            # If the backend is not Hugging Face, raise a NotImplementedError
            raise NotImplementedError(
                f'Currently .map is not supported for backend "{backend}"'
            )


    def get_backend(self) -> Optional[str]:
        r"""
        Returns
        ---------

        self.backend
        """
        return self.backend


    def get_backend_dataset(self):
        r"""
        Returns
        ---------

        self.backend_dataset
        """
        return self.backend_dataset

    
    def get_data_args(self):
        r"""
        Returns
        ---------

        self.data_args
        """
        return self.data_args


    def get_type(self):
        r"""
        Returns
        ---------

        self.type
        """
        return self.type