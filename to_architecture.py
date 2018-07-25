import argparse
import os
import shutil
from xml.dom import minidom


def is_processed(suite_name, append):
    if suite_name.endswith(append):
        print "File has already been processed with %s" % append
        return True
    return False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This script aims to append some tokens at the end of test suite names within JUnit XML files.")
    parser.add_argument("file",
                        help="File to be processed")
    parser.add_argument("append",
                        help="String to be appended to test suite name")
    parser.add_argument("--type", "-t", choices=["lua", "googletest"], required=True,
                        help="Input file type: can be lua|googletest")
    parser.add_argument("--revert", "-r", action="store_true",
                        help="If this option is passed, the backup file is restored")
    args = parser.parse_args()

    if args.revert:
        shutil.copy2(args.file + ".tmp", args.file)
        print "%s restored to %s" % (args.file + ".tmp", args.file)
        print "No more actions will be done"
    else:
        if os.path.isfile(args.file):
            shutil.copy2(args.file, args.file + ".tmp")
            print "%s backed up to %s" % (args.file, args.file + ".tmp")
        else:
            print "%s does not exits. Indicate an existing file!" % args.file
            exit(1)
        dom = minidom.parse(args.file)
        if args.type == "lua":
            for e in dom.getElementsByTagName("testcase"):
                suite_name = e.getAttribute("classname")
                if is_processed(suite_name, args.append):
                    exit(0)
                suite_tgt = "%s_%s" % (suite_name, args.append)
                e.setAttribute("classname", suite_tgt)
                test_name = e.getAttribute("name")
                e.setAttribute("name", test_name.replace(suite_name, suite_tgt))
            with open(args.file, 'w') as f:
                dom.writexml(f)
        elif args.type == "googletest":
            for e in dom.getElementsByTagName("testsuite"):
                suite_name = e.getAttribute("name")
                if is_processed(suite_name, args.append):
                    exit(0)
                suite_tgt = "%s_%s" % (suite_name, args.append)
                e.setAttribute("name", suite_tgt)
                for case in e.getElementsByTagName("testcase"):
                    case.setAttribute("classname", suite_tgt)
            with open(args.file, 'w') as f:
                dom.writexml(f)
        else:
            print "Wrong type. Cannot determine action to do. Select an admissible type between lua|googletest"
            exit(1)
        print "%s appended to every test suite reference within %s" % (args.append, args.file)
    exit(0)


