import subprocess
import logging


class Runner():
    def run_script(self, script_string, assert_result_function):
        """
        Run the script and check if it succeeds or not 
        using the *assert_result_function*.
        Download product and check if the operation succeed or not.
        :param script_string: the script string to be launched
        :param assert_result_function: check if ran script produced the correct result or not
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
        return assert_result_function(output, p)
