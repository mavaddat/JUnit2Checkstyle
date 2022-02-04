import argparse
import os
import shutil
from xml.dom import minidom
import re


def is_processed(suite_name, append):
    if suite_name.endswith(append):
        print("File has already been processed with %s" % append)
        return True
    return False


def backup_filename(file):
    return "%s.tmp" % file


def save(file, dom):
    if os.path.isfile(file):
        bkp = backup_filename(file)
        shutil.copy2(file, bkp)
        print("%s backed up to %s" % (file, bkp))
    else:
        print("%s does not exist. Indicate an existing file!" % file)
        exit(1)
    with open(file, 'w') as f:
        dom.writexml(f)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This script aims to append some tokens at the end of test suite names within JUnit XML files.")
    parser.add_argument("file",
                        help="File to be processed")
    parser.add_argument("--token",
                        help="Token to be appended to test suite name. If this option is not passed, the script will infer the token from the filename.")
    parser.add_argument("--type", "-t", choices=["lua", "googletest"], required=True,
                        help="Input file type: can be lua|googletest")
    parser.add_argument("--revert", "-r", action="store_true",
                        help="If this option is passed, the backup file is restored")
    args = parser.parse_args()

    if args.revert:
        bkp = backup_filename(args.file)
        if os.path.isfile(bkp):
            shutil.copy2(bkp, args.file)
            print("%s restored to %s" % (bkp, args.file))
            print("No more actions will be done")
        else:
            print("No backup file found")
        exit(0)
    else:
        if args.token is None:
            try:
                token = re.search("\w*_(\w*)(.\w*)?(?!\S)", args.file).group(1)
                print("Auto-detected token: %s" % token)
            except AttributeError:
                print("Unable to autodetermine token to append. Please provide a token with --token option.")
                exit(1)
        else:
            token = args.token
        try:
            dom = minidom.parse(args.file)
        except IOError:
            print("%s does not exist" % args.file)
            exit(1)
        if args.type == "lua":
            for e in dom.getElementsByTagName("testcase"):
                suite_name = e.getAttribute("classname")
                if is_processed(suite_name, token):
                    exit(0)
                suite_tgt = "%s_%s" % (suite_name, token)
                e.setAttribute("classname", suite_tgt)
                test_name = e.getAttribute("name")
                e.setAttribute("name", test_name.replace(suite_name, suite_tgt))
        elif args.type == "googletest":
            for e in dom.getElementsByTagName("testsuite"):
                suite_name = e.getAttribute("name")
                if is_processed(suite_name, token):
                    exit(0)
                suite_tgt = "%s_%s" % (suite_name, token)
                e.setAttribute("name", suite_tgt)
                for case in e.getElementsByTagName("testcase"):
                    case.setAttribute("classname", suite_tgt)
        else:
            print("Wrong type. Cannot determine action to do. Select an admissible type between lua|googletest")
            exit(1)

        save(args.file, dom)
        print("%s appended to every test suite reference within %s" % (token, args.file))
        exit(0)
