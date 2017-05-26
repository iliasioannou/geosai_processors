import subprocess


class Downloader():

    def download(self, scriptString):
        """
        Download product and check if the operation succeed or not.
        :param scriptString: the script string to be launched
        :return: a boolean value to check if downloaded has been correctly performed
        """
        p = subprocess.Popen(scriptString.split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        return True if "Download rate" in output and  p.returncode == 0 else False