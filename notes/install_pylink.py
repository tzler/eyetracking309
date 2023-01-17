from distutils.core import setup, Extension
from distutils.command.install_data import install_data
from distutils.command.install import install
from distutils.command.build import build
from distutils.command.build_py import build_py
import distutils.dir_util

import os
import sys
import struct
import glob
import tempfile


#data installer with improved intelligence over distutils
#data files are copied into the project directory instead
#of willy-nilly - stolen from pygame
class smart_install_data(install_data):
	def run(self):
		#need to change self.install_dir to the actual library dir
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return install_data.run(self)
		


class clean_install(install):
	def remove(self,path):
		print ("Removing " + path)
		if os.path.exists(path):
			if os.path.isfile(path):
				try:
					os.unlink(path)
				except:
					print('Unknown error during unlinking file '+ path +" (skipped)")				
			else:
				for libfile in os.listdir(path):
					subpath = os.path.join(path, libfile)
					try:
						if os.path.isfile(subpath):
							os.unlink(subpath)
						else:
							self.remove(subpath)
					except:
						print('Unknown error during removal of '+subpath +" (skipped)" )
				os.removedirs(path)
	
	def clean(self, installdir):
		listing = glob.glob(installdir+"/*pylink*")
		for filename in listing:
			self.remove(filename)

	def run(self):
		self.clean(self.install_lib)
		return install.run(self)

class dummy_build(build):
	def run(self):
		pass # nothing to build



if __name__ == "__main__":

	BUILDFOLDER= tempfile.gettempdir() + "/build"
	script_path = os.path.dirname(sys.argv[0])
	if len(script_path) != 0:
		os.chdir(script_path)
	
	if 'install' in sys.argv:
		sys.argv.remove('install') #if install is passsed in, remove it.
	if len(sys.argv) > 1:
		print ("usage: python install_pylink.py")
		exit(1)
	sys.argv.append('clean')
	sys.argv.append('--all')
	sys.argv.append('build')
	sys.argv.append('--build-lib='+BUILDFOLDER)	
	sys.argv.append('install')
	
	METADATA = {
	}


	data_files=[]
	bit = ''
	if sys.platform != 'darwin':
		bit = '32/'
		if (struct.calcsize('P')*8) > 32: bit = '64/'
	srcfldr='%s%d.%d/pylink'%(bit,sys.version_info[0],sys.version_info[1])

	sys.path.insert(1, srcfldr)
	verscript='''
import __version__ as v
METADATA['name']=v.__title__
METADATA['version']=v.__version__
METADATA['license']=v.__license__
METADATA['url']=v.__url__
METADATA['author']=v.__author__
METADATA['author_email']=v.__author_email__
METADATA['description']=v.__description__
'''
	exec(verscript)
	sys.path.remove(srcfldr)
	src_files = os.listdir(srcfldr) 
	for file_name in src_files:
		if "__pycache__" in file_name:
			continue
		elif file_name[-3:] != ".py":
			full_file_name = os.path.join(srcfldr, file_name)
			data_files.append(full_file_name)

				
	PACKAGEDATA = {
			"cmdclass":	{'install_data': smart_install_data, 'install': clean_install,'build': dummy_build},
			"packages":	['pylink'],
			"package_dir": {'pylink': srcfldr},
			"data_files":  [('pylink', data_files)],


	}


	PACKAGEDATA.update(METADATA)
	try:
		distutils.dir_util.remove_tree(BUILDFOLDER) #remove the build folder
	except:
		pass # no build folder at this time to clean
	setup(*[], **PACKAGEDATA)
	distutils.dir_util.remove_tree(BUILDFOLDER) #remove the build folder again

