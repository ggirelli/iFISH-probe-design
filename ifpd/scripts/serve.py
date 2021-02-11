"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
import bottle  # type: ignore
import ifpd
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
import os
from rich.logging import RichHandler  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="Run WebServer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Run WebServer.",
    )
    parser.add_argument(
        "static",
        metavar="folder",
        type=str,
        help="Path to static folder (created if not found).",
    )

    parser.add_argument(
        "-u",
        "--url",
        metavar="url",
        type=str,
        default="0.0.0.0",
        help="URL hosting the web server. Default: 0.0.0.0",
    )
    parser.add_argument(
        "-p",
        "--port",
        metavar="port",
        type=int,
        default=8080,
        help="Web server port. Default: 8080",
    )
    parser.add_argument(
        "-m",
        "--mail",
        metavar="email",
        type=str,
        default="email@example.com",
        help="Email address of server admin.",
    )
    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced.add_argument(
        "--hide-breadcrumbs",
        action="store_const",
        dest="show_breadcrumbs",
        const=False,
        default=True,
        help="""Hide navigation breadcrumbs.""",
    )
    advanced.add_argument(
        "-R",
        "--custom-routes",
        metavar="routesFile",
        type=str,
        help="Path to custom routes Python file.",
    )
    parser.add_argument(
        "-T",
        "--custom-templates",
        metavar="templateFolder",
        type=str,
        help="Path to folder with custom templates.",
    )
    parser.add_argument(
        "-H",
        "--homepage",
        metavar="homepageTemplate",
        type=str,
        help="""Name of homepage template. Homepage is off by default.
        Use "-H home_default" to turn default homepage template on.
        When using a custom homepage template, -T must be specified.""",
    )

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    return args


def add_static_routes_includes(root, root_path):
    # CSS files
    @root.route("/css/<path>")
    def callback_css(path):
        return bottle.static_file(path, "%s/interface/css/" % root_path)

    # JS files
    @root.route("/js/<path>")
    def callback_js(path):
        return bottle.static_file(path, "%s/interface/js/" % root_path)

    # Fonts files
    @root.route("/fonts/<path>")
    def callback_fonts(path):
        return bottle.static_file(path, "%s/interface/fonts/" % root_path)

    return root


def add_static_routes_download(root, root_path):
    # Images
    @root.route("/images/<path>")
    def callback_images(path):
        return bottle.static_file(path, "%s/interface/images/" % root_path)

    # Documents
    @root.route("/documents/<path>")
    def callback_documents(path):
        return bottle.static_file(path, "%s/interface/documents/" % root_path)

    return root


def build_root_app(args, home_template, home_status):
    # Server params
    root_path = "%s/" % os.path.dirname(ifpd.__file__)
    section_path = "%s/" % os.path.dirname(ifpd.sections.__file__)

    # Start root app
    root = bottle.Bottle()

    # Home
    @root.route("/")
    @bottle.view(home_template)
    def index():
        d = {}
        d["custom_stylesheets"] = ["home.css"]
        d["title"] = "iFISH"
        d["description"] = "iFISH"
        d["home_status"] = home_status
        return d

    # 404 Error
    @root.error(404)
    def error404(error):
        return "Nothing here, sorry :("

    root = add_static_routes_includes(root, root_path)
    root = add_static_routes_download(root, root_path)

    # Load Sections
    pdApp = ifpd.sections.probe_design.App(
        section_path,
        args.static,
        root_path,
        "http://%s:%d/" % (args.url, args.port),
        "probe-design/",
    )
    pdApp.admin_email = args.mail

    # Custom routes
    if args.custom_routes is not None:
        exec(open(args.custom_routes).read())

    pdApp.vd["breadcrumbs"] = args.show_breadcrumbs

    # Mount Sections
    root.mount("probe-design", pdApp)

    return root


def mk_missing_dirs(args):
    if not os.path.isdir(args.static):
        os.mkdir(args.static)
    if not os.path.isdir("%s/db" % args.static):
        os.mkdir("%s/db" % args.static)
    if not os.path.isdir("%s/query" % args.static):
        os.mkdir("%s/query" % args.static)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    # Server params
    root_path = "%s/" % os.path.dirname(ifpd.__file__)

    bottle.TEMPLATE_PATH.append(root_path)
    bottle.TEMPLATE_PATH.append("%s/interface/views/" % root_path)
    if args.custom_templates is not None:
        assert os.path.isdir(
            args.custom_templates
        ), f"folder not found: '{args.custom_templates}'"
        bottle.TEMPLATE_PATH.append(args.custom_templates)

    assert not os.path.isfile(args.static), (
        "folder expected, file found: %s" % args.static
    )
    mk_missing_dirs(args)

    if args.homepage is not None:
        if not "home_default.tpl.html" == args.homepage:
            assert (
                args.custom_templates is not None
            ), "-T option required when using -H."
        home_template = args.homepage
        home_status = True
    else:
        home_template = "home_default.tpl.html"
        home_status = False

    if args.custom_routes is not None:
        assert os.path.isfile(
            args.custom_routes
        ), f"file not found: {args.custom_routes}"

    root = build_root_app(args, home_template, home_status)

    # RUN ==========================================================================

    root.run(host=args.url, port=args.port, debug=True, server="paste")

    logging.info("Done. :thumbs_up: :smiley:")
