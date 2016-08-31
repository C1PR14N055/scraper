#!/usr/bin/python
import json, os, shutil, stat
from pprint import pprint #pretty print json

list_of_unique_acc_dir_parents = []
list_of_unique_acc_dirs = []

list_of_unique_cons_dir_parents = []
list_of_unique_cons_dirs = []

def get_cats():
    rootDir = './prod/'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print 'Found directory: %s' % dirName
        try:
            if dirName.index("/acc/"):
                if dirName[dirName.rindex("/"):] not in list_of_unique_acc_dirs:
                    list_of_unique_acc_dir_parents.append(dirName[:dirName.rindex("/")])
                    list_of_unique_acc_dirs.append(dirName[dirName.rindex("/"):])
        except:
            pass
        try:
            if dirName.index("/cons/"):
                if dirName[dirName.rindex("/"):] not in list_of_unique_cons_dirs:
                    list_of_unique_cons_dir_parents.append(dirName[:dirName.rindex("/")])
                    list_of_unique_cons_dirs.append(dirName[dirName.rindex("/"):])
        except:
            pass

    for i in range(len(list_of_unique_acc_dirs)):
        #print list_of_unique_acc_dir_parents[i] + list_of_unique_acc_dirs[i]
        print "MERGED ACC " + str(i) + " / " + str(len(list_of_unique_acc_dirs))
        copy_tree(list_of_unique_acc_dir_parents[i] + list_of_unique_acc_dirs[i], "unique_acc" + list_of_unique_acc_dirs[i])

    for i in range(len(list_of_unique_cons_dirs)):
        #print list_of_unique_cons_dir_parents[i] + list_of_unique_cons_dirs[i]
        print "MERGED CONS " + str(i) + " / " + str(len(list_of_unique_cons_dirs))
        copy_tree(list_of_unique_cons_dir_parents[i] + list_of_unique_cons_dirs[i], "unique_cons" + list_of_unique_cons_dirs[i])




def copy_tree(src, dst, symlinks = False, ignore = None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copy_tree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


get_cats()
#copy_tree("easy_upload", "test")