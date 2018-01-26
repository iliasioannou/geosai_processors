import json
import os


class StringScriptBuilder():
    """
    Build a string with all parameters set.
    Use setters to override default values (read by conf.json) file
    and provide these mandatory fields:
    
    - product name
    - dataset
    - start date
    - end date
    - options to be used
    - out file name
    """

    def build(self):
        conf_json_path = getattr(self, 'conf_path', 'conf.json')
        with open(os.path.join("product_downloader", "script", conf_json_path)) as inp:
            conf = json.loads(inp.read())
        return '/home/anaconda/bin/python2.7 %s -u %s -p %s -m %s -x %s -X %s -y %s -Y %s -z %s -Z %s -o %s -s %s -d %s -t "%s" -T "%s" -v %s -f %s' % (
            getattr(self, 'motu_client_path', conf['motu_client_path']),
            getattr(self, 'username', conf['username']),
            getattr(self, 'password', conf['password']),
            getattr(self, 'base_url', conf["base_url"]),
            getattr(self, 'x', conf['x']),
            getattr(self, 'X', conf['X']),
            getattr(self, 'y', conf['y']),
            getattr(self, 'Y', conf['Y']),
            getattr(self, 'z', conf['z']),
            getattr(self, 'Z', conf['Z']),
            getattr(self, 'output_path', conf['output_path']),
            self.product,
            self.dataset,
            self.dates[0],
            self.dates[1],
            " -v ".join(self.values),
            self.out_name
        )

    def set_credentials(self, username='dsykas1', password=''):
        self.username = username
        self.password = password
        return self

    def set_base_url(self, base_url):
        self.base_url = base_url
        return self

    def set_coordinates(self, *coords):
        self.x, self.X, self.y, self.Y = coords
        return self

    def set_output_path(self, output_path):
        self.output_path = output_path
        return self

    def set_motu_client(self, motu_client_path):
        self.motu_client_path = motu_client_path
        return self

    def set_dataset(self, dataset):
        self.dataset = dataset
        return self

    def set_product(self, product):
        self.product = product
        return self

    def set_values(self, values):
        self.values = values
        return self

    def set_dates(self, dates):
        self.dates = dates
        return self

    def set_depth(self, depth):
        self.depth = depth
        return self

    def set_out_name(self, out_name):
        self.out_name = out_name
        return self

    def set_conf(self, conf_path):
        self.conf_path = conf_path
        return self
