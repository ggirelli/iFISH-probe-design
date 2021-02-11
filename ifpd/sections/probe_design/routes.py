"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import bottle as bot  # type: ignore
import configparser
import datetime
import hashlib
import ifpd as fp
from ifpd.sections import routes
from ifpd.sections.probe_design.query import Query
import os
import pandas as pd  # type: ignore
import shlex
import time
from typing import Dict
import zipfile


def zipFile(path, ziph, root=None):
    """Zips a file.
    Args:
            path (string): file path.
            ziph (Zipfile): zipfile handler.
    Returns:
            None.
    """
    assert os.path.isfile(path), "file expected."
    oldRoot = ""
    new_path = path
    if not type(None) == type(root):
        oldRoot = os.path.commonpath([root, path])
        if 0 != len(oldRoot):
            if new_path.startswith(oldRoot):
                new_path = new_path[len(oldRoot) :]
    ziph.write(path, new_path)


def zipDir(path, ziph, mainRoot=None):
    """Zips a directory. Based on https://goo.gl/GeCPVm.
    Args:
            path (string): directory path.
            ziph (Zipfile): zipfile handler.
    Returns:
            None.
    """

    assert os.path.isdir(path), "folder expected."
    for root, dirs, files in os.walk(path):
        for file in files:
            zipFile(os.path.join(root, file), ziph, mainRoot)


class Routes(routes.Routes):
    """Routes class."""

    # Empty routes dictionary
    data: Dict = {}
    zipDirName = "zips"

    def __init__(self):
        """
        Create new routes here using the add_route method.
        """

        # Set default Routes
        super(Routes, self).__init__()

        # Static files ---------------------------------------------------------

        route = "/q/<query_id>/download/"
        self.add_route("query_download", "route", route)

        dname = ("<dname:re:(images|documents)>",)
        route = "/q/<query_id>/c/<candidate_id>/%s/<path>" % dname
        self.add_route("candidate_static_file", "route", route)
        route = "/q/<query_id>/c/<candidate_id>/documents/"
        route += "<path:re:.*>/download/"
        self.add_route("candidate_static_file_download", "route", route)
        route = "/q/<query_id>/c/<candidate_id>/download/"
        self.add_route("candidate_download", "route", route)

        dname = ("<dname:re:(images|documents)>",)
        route = "/q/<query_id>/cs/<candidate_id>/%s/<path>" % dname
        self.add_route("candidate_set_static_file", "route", route)
        route = "/q/<query_id>/cs/<candidate_id>/documents/"
        route += "<path:re:.*>/download/"
        self.add_route("candidate_set_static_file_download", "route", route)
        route = "/q/<query_id>/cs/<candidate_id>/download/"
        self.add_route("candidate_set_download", "route", route)

        dname = ("<dname:re:(images|documents)>",)
        route = "/q/<query_id>/cs/<candidate_id>/p/<probe_id>/%s/<path>" % dname
        self.add_route("candidate_set_probe_static_file", "route", route)
        route = "/q/<query_id>/cs/<candidate_id>/p/<probe_id>/documents/"
        route += "<path:re:.*>/download/"
        self.add_route("candidate_set_probe_static_file_download", "route", route)
        route = "/q/<query_id>/cs/<candidate_id>/p/<probe_id>/download/"
        self.add_route("candidate_set_probe_download", "route", route)

        # Pages ----------------------------------------------------------------

        self.add_route("home", "route", "")
        self.add_route("home", "route", "/")
        self.add_route("home", "view", "home.tpl.html")

        self.add_route("query", "route", "/q/<query_id>")
        self.add_route("query", "view", "query.tpl.html")

        uri = "/q/<query_id>/c/<candidate_id>"
        self.add_route("candidate_probe", "route", uri)
        self.add_route("candidate_probe", "view", "candidate_probe.tpl.html")

        uri = "/q/<query_id>/cs/<candidate_id>"
        self.add_route("candidate_set", "route", uri)
        self.add_route("candidate_set", "view", "candidate_set.tpl.html")

        uri = "/q/<query_id>/cs/<candidate_id>/p/<probe_id>"
        self.add_route("candidate_set_probe", "route", uri)
        self.add_route("candidate_set_probe", "view", "candidate_set_probe.tpl.html")

        # Forms ----------------------------------------------------------------

        self.add_route("single_query", "post", "/single_query")

        self.add_route("spotting_query", "post", "/spotting_query")

        self.add_route("single_queries", "post", "/single_queries")

        self.add_route("hide_alert", "post", "/hide_alert")

        # Errors ---------------------------------------------------------------

        self.add_route("error404", "error", 404)
        self.add_route("error500_with_redirect", "error", 500)

        # AJAX requests --------------------------------------------------------

        self.add_route("list_chromosomes", "get", "/listChr/<dbDir>")
        self.add_route("queueStatus", "get", "/queueStatus")

        return

    def mkZipDir(routes, self):
        zipDirPath = os.path.join(self.static_path, "query", routes.zipDirName)
        if not os.path.isdir(zipDirPath):
            os.mkdir(zipDirPath)

    def zipQuery(routes, self, query_id):
        zipDirPath = os.path.join(self.static_path, "query", routes.zipDirName)
        zipPath = os.path.join(zipDirPath, f"{query_id}.zip")
        zipf = zipfile.ZipFile(zipPath, "w", zipfile.ZIP_DEFLATED)
        zipDir(
            os.path.join(self.static_path, "query", query_id),
            zipf,
            os.path.join(self.static_path, "query"),
        )
        zipFile(
            os.path.join(self.static_path, "query", f"{query_id}.config"),
            zipf,
            os.path.join(self.static_path, "query"),
        )
        zipf.close()

    def zipCandidate(routes, self, query_id, candidate_id):
        zipDirPath = os.path.join(self.static_path, "query", routes.zipDirName)
        zipPath = os.path.join(zipDirPath, f"{query_id}.candidate_{candidate_id}.zip")
        zipf = zipfile.ZipFile(zipPath, "w", zipfile.ZIP_DEFLATED)
        zipDir(
            os.path.join(
                self.static_path, "query", query_id, f"candidate_{candidate_id}"
            ),
            zipf,
            os.path.join(
                self.static_path, "query", query_id, f"candidate_{candidate_id}"
            ),
        )
        zipf.close()

    def zipCandidateSet(routes, self, query_id, candidate_id):
        zipDirPath = os.path.join(self.static_path, "query", routes.zipDirName)
        zipPath = os.path.join(zipDirPath, f"{query_id}.probe_set_{candidate_id}.zip")
        zipf = zipfile.ZipFile(zipPath, "w", zipfile.ZIP_DEFLATED)
        zipDir(
            os.path.join(
                self.static_path, "query", query_id, f"probe_set_{candidate_id}"
            ),
            zipf,
            os.path.join(
                self.static_path, "query", query_id, f"probe_set_{candidate_id}"
            ),
        )
        zipf.close()

    def zipCandidateSetProbe(routes, self, query_id, candidate_id, probe_id):
        zipDirPath = os.path.join(self.static_path, "query", routes.zipDirName)
        zipPath = os.path.join(
            zipDirPath, f"{query_id}.probe_set_{candidate_id}.probe_{probe_id}.zip"
        )
        zipf = zipfile.ZipFile(zipPath, "w", zipfile.ZIP_DEFLATED)
        zipDir(
            os.path.join(
                self.static_path,
                "query",
                query_id,
                f"probe_set_{candidate_id}",
                f"probe_{probe_id}",
            ),
            zipf,
            os.path.join(
                self.static_path,
                "query",
                query_id,
                f"probe_set_{candidate_id}",
                f"probe_{probe_id}",
            ),
        )
        zipf.close()

    # Static files -------------------------------------------------------------

    def candidate_static_file(routes, self, query_id, candidate_id, dname, path):
        """Access candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/candidate_%s/" % (self.static_path, query_id, candidate_id)
        return bot.static_file(path, ipath)

    def candidate_static_file_download(routes, self, query_id, candidate_id, path):
        """Download candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/candidate_%s/" % (self.static_path, query_id, candidate_id)
        outname = "%s.%s" % (query_id, path)
        return bot.static_file(path, ipath, download=outname)

    def candidate_set_static_file(routes, self, query_id, candidate_id, dname, path):
        """Access candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/probe_set_%s/" % (self.static_path, query_id, candidate_id)
        return bot.static_file(path, ipath)

    def candidate_set_static_file_download(routes, self, query_id, candidate_id, path):
        """Download candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/probe_set_%s/" % (self.static_path, query_id, candidate_id)
        outname = "%s.%s" % (query_id, path)
        return bot.static_file(path, ipath, download=outname)

    def candidate_set_probe_static_file(
        routes, self, query_id, candidate_id, probe_id, dname, path
    ):
        """Access candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/probe_set_%s/probe_%s/" % (
            self.static_path,
            query_id,
            candidate_id,
            probe_id,
        )
        return bot.static_file(path, ipath)

    def candidate_set_probe_static_file_download(
        routes, self, query_id, candidate_id, probe_id, path
    ):
        """Download candidate static files.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
                dname (string): file type.
                path (string): file name.
        """
        ipath = "%s/query/%s/probe_set_%s/probe_%s/" % (
            self.static_path,
            query_id,
            candidate_id,
            probe_id,
        )
        outname = "%s.probe_set_%s.%s" % (query_id, candidate_id, path)
        return bot.static_file(path, ipath, download=outname)

    def query_download(routes, self, query_id):
        """Download compressed query output.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
        """

        routes.mkZipDir(self)
        ipath = os.path.join(self.static_path, "query", routes.zipDirName)
        fName = f"{query_id}.zip"
        outname = f"query.{fName}"

        if not os.path.isfile(os.path.join(ipath, fName)):
            routes.zipQuery(self, query_id)

        return bot.static_file(fName, ipath, download=outname)

    def candidate_download(routes, self, query_id, candidate_id):
        """Download compressed candidate output.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        routes.mkZipDir(self)
        ipath = os.path.join(self.static_path, "query", routes.zipDirName)
        fName = f"{query_id}.candidate_{candidate_id}.zip"
        outname = f"query.{fName}"

        if not os.path.isfile(os.path.join(ipath, fName)):
            routes.zipCandidate(self, query_id, candidate_id)

        return bot.static_file(fName, ipath, download=outname)

    def candidate_set_download(routes, self, query_id, candidate_id):
        """Download compressed candidate output.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        routes.mkZipDir(self)
        ipath = os.path.join(self.static_path, "query", routes.zipDirName)
        fName = f"{query_id}.probe_set_{candidate_id}.zip"
        outname = f"query.{fName}"

        if not os.path.isfile(os.path.join(ipath, fName)):
            routes.zipCandidateSet(self, query_id, candidate_id)

        return bot.static_file(fName, ipath, download=outname)

    def candidate_set_probe_download(routes, self, query_id, candidate_id, probe_id):
        """Download compressed candidate output.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        routes.mkZipDir(self)
        ipath = os.path.join(self.static_path, "query", routes.zipDirName)
        fName = f"{query_id}.probe_set_{candidate_id}.probe_{probe_id}.zip"
        outname = f"query.{fName}"

        if not os.path.isfile(os.path.join(ipath, fName)):
            routes.zipCandidateSetProbe(self, query_id, candidate_id, probe_id)

        return bot.static_file(fName, ipath, download=outname)

    # Pages --------------------------------------------------------------------

    def home(routes, self):
        """Home-page.

        Args:
                self (App): ProbeDesigner.App instance.
        """

        d = self.vd

        d["title"] = self.tprefix + "Home"
        d["custom_stylesheets"] = ["home.css", "style.css"]
        d["custom_root_stylesheets"] = []

        configPathList = [
            os.path.join(self.static_path, "db", p, ".config")
            for p in next(os.walk(os.path.join(self.static_path, "db")))[1]
        ]
        configPathList.sort()
        d["dbdata"] = []
        for configPath in configPathList:
            with open(configPath, "r") as IH:
                parser = configparser.ConfigParser()
                parser.read_string("".join(IH.readlines()))
                d["dbdata"].append(parser)
        d["dblist"] = {}
        for p in d["dbdata"]:
            dbDir = os.path.basename(p["SOURCE"]["outdirectory"])
            dbName = p["DATABASE"]["name"]
            d["dblist"][dbName] = dbDir

        return d

    def query(routes, self, query_id):
        """Query output page.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
        """

        d = self.vd

        d["title"] = "%s Query: %s" % (self.tprefix, query_id)
        d["custom_stylesheets"] = ["query.css", "style.css"]
        d["custom_root_stylesheets"] = []

        d["query"] = Query(query_id, self.qpath).data
        d["queryRoot"] = self.qpath

        if "done" == d["query"]["status"]:
            if "single" == d["query"]["type"]:
                fpath = os.path.join(self.qpath, query_id, "candidates.tsv")
            elif "spotting" == d["query"]["type"]:
                fpath = os.path.join(self.qpath, query_id, "set_candidates.tsv")
            if not os.path.isfile(fpath):
                d["query"]["status"] = "error"
            else:
                d["query"]["candidate_table"] = pd.read_csv(fpath, "\t")

        d["queryTimeout"] = 24 * 60 * 60  # 1 day timeout

        d["admin_email"] = self.admin_email

        return d

    def candidate_probe(routes, self, query_id, candidate_id):
        """Candidate output page.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        d = self.vd

        d["title"] = "%s Query: %s" % (self.tprefix, query_id)
        d["custom_stylesheets"] = ["query.css", "style.css"]
        d["custom_root_stylesheets"] = []

        d["query"] = Query(query_id, self.qpath).data
        d["queryRoot"] = self.qpath

        d["candidate"] = {"id": candidate_id}
        configPath = os.path.join(
            self.qpath,
            query_id,
            f"candidate_{candidate_id}",
            f"candidate_{candidate_id}.config",
        )
        with open(configPath, "r") as IH:
            config = configparser.ConfigParser()
            config.read_string("".join(IH.readlines()))
            d["candidate"].update(config["REGION"].items())
            d["candidate"].update(config["PROBE"].items())
            d["candidate"].update(config["FEATURES"].items())

        return d

    def candidate_set(routes, self, query_id, candidate_id):
        """Candidate output page.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        d = self.vd

        d["title"] = "%s Query: %s" % (self.tprefix, query_id)
        d["custom_stylesheets"] = ["query.css", "style.css"]
        d["custom_root_stylesheets"] = []

        d["query"] = Query(query_id, self.qpath).data
        d["queryRoot"] = self.qpath
        d["query"]["candidate_table"] = pd.read_csv(
            os.path.join(self.qpath, query_id, "set_candidates.tsv"), "\t"
        )

        d["candidate"] = {"id": candidate_id}

        return d

    def candidate_set_probe(routes, self, query_id, candidate_id, probe_id):
        """Candidate output page.

        Args:
                self (App): ProbeDesigner.App instance.
                query_id (string): query folder name.
                candidate_id (string): candidate folder name.
        """

        d = self.vd

        d["title"] = "%s Query: %s" % (self.tprefix, query_id)
        d["custom_stylesheets"] = ["query.css", "style.css"]
        d["custom_root_stylesheets"] = []

        d["query"] = Query(query_id, self.qpath).data
        d["queryRoot"] = self.qpath
        d["query"]["candidate_table"] = pd.read_csv(
            os.path.join(self.qpath, query_id, "set_candidates.tsv"), "\t"
        )

        d["candidate"] = {"id": candidate_id}

        d["probe"] = {"id": probe_id}
        configPath = os.path.join(
            self.qpath,
            query_id,
            f"probe_set_{candidate_id}",
            f"probe_{probe_id}",
            f"probe_{probe_id}.config",
        )
        with open(configPath, "r") as IH:
            config = configparser.ConfigParser()
            config.read_string("".join(IH.readlines()))
            d["probe"].update(config["REGION"].items())
            d["probe"].update(config["PROBE"].items())
            d["probe"].update(config["FEATURES"].items())

        return d

    # Form reception -----------------------------------------------------------

    def hide_alert(routes, self):
        """Hide bookmark alert for a specific query.

        Args:
                self (App): ProbeDesigner.App instance.
        """

        formData = bot.request.forms

        Query(formData.query_id, self.qpath).data
        config = configparser.ConfigParser()
        configPath = os.path.join(self.qpath, f"{formData.query_id}.config")
        with open(configPath, "r") as IH:
            config.read_string("".join(IH.readlines()))
        config["GENERAL"]["hidden_bookmark_alter"] = "True"
        with open(configPath, "w+") as OH:
            config.write(OH)

        return "Done"

    def single_query(routes, self):
        """Single probe query form reception route.

        Args:
                self (App): ProbeDesigner.App instance.
        """

        formData = bot.request.forms
        queriedRegion = ""
        if formData.start != formData.end:
            queriedRegion = f"--region {formData.start} {formData.end}"
        query_id = "%s:%s:%s:%s" % (
            formData.chromosome,
            formData.start,
            formData.end,
            time.time(),
        )
        encoder = hashlib.sha256()
        encoder.update(bytes(query_id, "utf-8"))
        query_id = encoder.hexdigest()

        dbPath = f"{self.static_path}/db/{formData.database}"
        oligoDB = fp.query.OligoDatabase(dbPath)
        min_dist = oligoDB.get_oligo_min_dist()

        cmd = [
            "ifpd",
            "query",
            "probe",
            shlex.quote(dbPath),
            shlex.quote(formData.chromosome),
            shlex.quote(f"{self.static_path}/query/{query_id}"),
            "--order",
            shlex.quote(formData.f1),
            shlex.quote(formData.f2),
            shlex.quote(formData.f3),
            "--filter-thr",
            shlex.quote(formData.f1_threshold),
            "--n-oligo",
            shlex.quote(formData.n_oligo),
            "--max-probes",
            shlex.quote(formData.max_probes),
            "--min-d",
            shlex.quote(f"{min_dist}"),
        ]
        if 0 != len(queriedRegion):
            cmd.extend([shlex.quote(queriedRegion)])

        config = configparser.ConfigParser()
        timestamp = time.time()
        config["GENERAL"] = {
            "name": formData.name,
            "description": formData.description,
            "type": "single",
            "cmd": " ".join(cmd),
            "status": "queued",
        }
        config["WHEN"] = {
            "time": timestamp,
            "isotime": datetime.datetime.fromtimestamp(timestamp).isoformat(),
        }
        config["WHERE"] = {"db": formData.database, "region": queriedRegion}
        config["WHAT"] = {
            "n_oligo": formData.n_oligo,
            "threshold": formData.f1_threshold,
            "max_probes": formData.max_probes,
        }
        config["HOW"] = {"f1": formData.f1, "f2": formData.f2, "f3": formData.f3}
        configPath = os.path.join(self.static_path, "query", f"{query_id}.config")
        with open(configPath, "w+") as OH:
            config.write(OH)

        self.queue.put(cmd)

        bot.response.status = 303
        bot.response.set_header(
            "Location", f"{self.root_uri}{self.app_uri}q/{query_id}"
        )

        return "Query received."

    def spotting_query(routes, self):
        """Multi probe query form reception route.

        Args:
                self (App): ProbeDesigner.App instance.
        """

        formData = bot.request.forms
        queriedRegion = ""
        if formData.multi_start != formData.multi_end:
            queriedRegion = f"--region {formData.multi_start} {formData.multi_end}"
        query_id = "%s:%s:%s:%s" % (
            formData.multi_chromosome,
            formData.multi_start,
            formData.multi_end,
            time.time(),
        )
        encoder = hashlib.sha256()
        encoder.update(bytes(query_id, "utf-8"))
        query_id = encoder.hexdigest()

        dbPath = f"{self.static_path}/db/{formData.multi_database}"
        oligoDB = fp.query.OligoDatabase(dbPath)
        min_dist = oligoDB.get_oligo_min_dist()

        cmd = [
            "ifpd",
            "query",
            "set",
            shlex.quote(dbPath),
            shlex.quote(formData.multi_chromosome),
            shlex.quote(f"{self.static_path}/query/{query_id}"),
            shlex.quote(formData.multi_n_probes),
            "--order",
            shlex.quote(formData.f1),
            shlex.quote(formData.f2),
            shlex.quote(formData.f3),
            "--filter-thr",
            shlex.quote(formData.multi_f1_threshold),
            "--n-oligo",
            shlex.quote(formData.multi_n_oligo),
            "--min-d",
            shlex.quote(f"{min_dist}"),
            "--window-shift",
            shlex.quote(f"{formData.multi_win_shift}"),
        ]
        if 0 != len(queriedRegion):
            cmd.extend([shlex.quote(queriedRegion)])

        config = configparser.ConfigParser()
        timestamp = time.time()
        config["GENERAL"] = {
            "name": formData.multi_name,
            "description": formData.multi_description,
            "type": "spotting",
            "cmd": " ".join(cmd),
            "status": "queued",
        }
        config["WHEN"] = {
            "time": timestamp,
            "isotime": datetime.datetime.fromtimestamp(timestamp).isoformat(),
        }
        config["WHERE"] = {"db": formData.multi_database, "region": queriedRegion}
        config["WHAT"] = {
            "n_oligo": formData.multi_n_oligo,
            "threshold": formData.multi_f1_threshold,
            "n_probes": formData.multi_n_probes,
            "window_shift": formData.multi_win_shift,
        }
        config["HOW"] = {"f1": formData.f1, "f2": formData.f2, "f3": formData.f3}
        configPath = os.path.join(self.static_path, "query", f"{query_id}.config")
        with open(configPath, "w+") as OH:
            config.write(OH)

        self.queue.put(cmd)

        bot.response.status = 303
        bot.response.set_header(
            "Location", f"{self.root_uri}{self.app_uri}q/{query_id}"
        )

        # Output
        return "Query received."

    # Error --------------------------------------------------------------------

    def error500_with_redirect(routes, self, error):
        """Error 500.

        Args:
                self (App): ProbeDesigner.App instance.
                error: error data.
        """
        return f"""
        ERROR 500: nothing here, sorry :(<br/>
        Redirecting to homepage in 5 seconds.<br />
        <a href='{self.root_uri}{self.app_uri}'>Click here if you are stuck.</a>
        <meta http-equiv="refresh" content="5;url={self.root_uri}{self.app_uri}">
        """

    # AJAX Requests ------------------------------------------------------------

    def list_chromosomes(routes, self, dbDir):
        dbPath = os.path.join(self.static_path, "db", dbDir)
        chrList = [x for x in os.listdir(dbPath) if not os.path.isdir(x)]
        chrList = [x for x in chrList if x not in [".log", ".config"]]
        if 0 == len(chrList):
            return '{"chrList":[]}'
        chrList.sort()
        return '{"chrList":["%s"]}' % '","'.join(chrList[::-1])

    def queueStatus(routes, self):
        taskList = []
        for task in self.queue.queue:
            if "ifpd_query_set" == task[0]:
                outdir_id = 4
            elif "ifpd_query_probe" == task[0]:
                outdir_id = 3
            query_id = os.path.basename(task[outdir_id])
            data = Query(query_id, self.qpath).data
            taskList.append(os.path.basename(task[1]) + f' @{data["isotime"]}')
        if 0 == len(taskList):
            return '{"queue":[]}'
        return '{"queue": ["%s"]}' % '", "'.join(taskList)
