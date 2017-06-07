import subprocess
import logging


class Downloader():
    def download(self, script_string):
        """
        Download product and check if the operation succeed or not.
        :param script_string: the script string to be launched
        :return: a boolean value to check if downloaded has been correctly performed
        """
        p = subprocess.Popen(
            script_string,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True
        )
        output, err = p.communicate()
        return True if "Done" in output and p.returncode == 0 else False
