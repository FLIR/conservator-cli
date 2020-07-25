import os
import subprocess
import shutil

from FLIR.common.lib.execute_command import execute_command
from FLIR.conservator_cli.lib.graphql_api import get_datasets_from_search
from FLIR.conservator_cli.lib.conservator_credentials import ConservatorCredentials

python_command = "python" if os.name == "nt" else "python3"

class DatasetCache:
    def __init__(self, cache_path, credentials):
        self.cache_path = cache_path
        self.credentials = credentials

    def _pull_checkout_dataset(self, id, name, dataset_version):
        parent_folder = self.cache_path
        email = self.credentials.email.replace("@", "%40")
        print(email)
        if not id and name:
            id = self._get_dataset_id(name)
        if not id:
            raise Exception("could not find dataset with name {}".format(name))
        save = os.getcwd()
        os.chdir(parent_folder)


        if not os.path.exists(name):
            subp = subprocess.call(["git", "clone", "https://{}@flirconservator.com/git/dataset_{}".format(email, id), "{}".format(name)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.chdir(name)
            subp = subprocess.call([python_command, "./cvc.py", "remote", "add", "https://{}:{}@flirconservator.com/dvc".format(email, self.credentials.token)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.chdir("..")

        os.chdir(name)
        dataset_version_completed_process = subprocess.run(["git", "rev-parse", dataset_version], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if dataset_version_completed_process.returncode != 0:
            print(dataset_version_completed_process.stderr)
            quit(1);
        dataset_version = dataset_version_completed_process.stdout.decode("utf-8")[:-1]
        subp = subprocess.call(["git", "fetch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subp = subprocess.call(["git", "checkout", dataset_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subp = subprocess.call([python_command, "./cvc.py", "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subp = subprocess.call([python_command, "./cvc.py", "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(save)
        return dataset_version

    def _fetch_dataset(self, id, name, dataset_version):
        parent_folder = self.cache_path
        email = self.credentials.email.replace("@", "%40")
        print(email)
        if not id and name:
            id = self._get_dataset_id(name)
        if not id:
            raise Exception("could not find dataset with name {}".format(name))
        save = os.getcwd()
        os.chdir(parent_folder)

        if not os.path.exists(name):
            subp = subprocess.call(["git", "clone", "https://{}@flirconservator.com/git/dataset_{}".format(email, id), "{}".format(name)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.chdir(name)
            subp = subprocess.call([python_command, "./cvc.py", "remote", "add", "https://{}:{}@flirconservator.com/dvc".format(email, self.credentials.token)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.chdir("..")

        os.chdir(name)
        subp = subprocess.call(["git", "fetch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dataset_version_completed_process = subprocess.run(["git", "rev-parse", dataset_version], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if dataset_version_completed_process.returncode != 0:
            print(dataset_version_completed_process.stderr)
            quit(1);
        dataset_version = dataset_version_completed_process.stdout.decode("utf-8")[:-1]
        os.chdir(save)
        return dataset_version

    def _get_dataset_id(self, name):
        results = get_datasets_from_search(name, self.credentials.token)
        for result in results:
            if result["name"] == name:
                return result["id"]
        return None

    def git_rev_parse(self, dataset_name, dataset_version):
        dataset_version = self._fetch_dataset(None, dataset_name, dataset_version)
        return dataset_version

    def get_index_filepath(self, dataset_name, dataset_version):
        dataset_version = self._fetch_dataset(None, dataset_name, dataset_version)
        cached_index_path = os.path.join(self.cache_path, ".version", dataset_name, dataset_version, "index.json")
        if os.path.exists(cached_index_path):
            return cached_index_path

        dataset_version = str(self._pull_checkout_dataset(None, dataset_name, dataset_version))

        os.makedirs(os.path.dirname(cached_index_path), exist_ok=True)
        subp = subprocess.call(["cp", os.path.join(self.cache_path, dataset_name, "index.json"), cached_index_path], stdout=subprocess.DEVNULL)
        return cached_index_path

    def get_data_folder(self, dataset_name, dataset_version):
        dataset_version = self._fetch_dataset(None, dataset_name, dataset_version)
        cached_data_path = os.path.join(self.cache_path, ".version", dataset_name, dataset_version, "data")
        if os.path.exists(cached_data_path):
            return cached_data_path

        dataset_version = str(self._pull_checkout_dataset(None, dataset_name, dataset_version))

        os.makedirs(os.path.dirname(cached_data_path), exist_ok=True)
        source = os.path.abspath(os.path.dirname(cached_data_path))
        sink = os.path.abspath(os.path.join(self.cache_path, dataset_name, "data"))
        target_path = os.path.relpath(sink, start=source)
        subp = subprocess.call(["ln", "-s", target_path, cached_data_path], stdout=subprocess.DEVNULL)
        return cached_data_path
