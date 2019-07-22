from ftplib import FTP_TLS
from django.conf import settings
import logging
from . import helper
import os
import paramiko

comp_logger = logging.getLogger(__name__)


def copy_ftp_file(project_id, client_name, file_name):		#
	"""
	ftp file copy
	"""
	ftp =  FTP_TLS(settings.FTP_LOCATION)
	ftp.sendcmd("USER {}".format(settings.FTP_USER))
	ftp.sendcmd("PASS {}".format(settings.FTP_PASS))
	comp_logger.info('Initiating ftp file transfer for file {} for client {}'.format(file_name, client_name))
	ftp.cwd(client_name)

	# create project input dir
	project_dir = os.path.join(settings.PROJECT_DIR,str(project_id))
	helper.create_dir(project_dir)

	# copy remote ftp file to local project folder
	file_format = file_name.split('.')[-1]
	local_filename = os.path.join(settings.PROJECT_INPUT_FOLDER, '{}.{}'.format(project_id, file_format))

	if os.path.exists(local_filename):
		os.remove(local_filename)

	# project_input_dir = os.path.join(project_dir, settings.PROJECT_INPUT_FOLDER)
	# helper.create_dir(project_input_dir)
	# local_filename = os.path.join(project_input_dir, file_name)

	lf = open(local_filename, "wb")
	ftp.retrbinary("RETR " + file_name, lf.write, 8*1024)
	lf.close()
	comp_logger.info('Completed Copying file {} for client {}'.format(file_name, client_name))


def copy_ftp_file_over_sftp_using_key(remote_src_file_loc, local_dest_file_loc):
	"""
	ftp file copy over sftp using key based authentication
	"""
	comp_logger.info('Initiating ftp file transfer for src file:{} and dest file:{}'.format(remote_src_file_loc, local_dest_file_loc))
	ssh_client=paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())			# enable the host machine to trust remote machine

	ssh_client.connect(hostname=settings.FTP_LOCATION,username=settings.FTP_USER,key_filename=settings.FTP_KEY_PATH, timeout=settings.FTP_TIMEOUT)

	# file copy
	ftp_client=ssh_client.open_sftp()
	

	ftp_client.get(remote_src_file_loc,local_dest_file_loc)
	ftp_client.close()

	comp_logger.info('Completed ftp file transfer for src file:{} and dest file:{}'.format(remote_src_file_loc, local_dest_file_loc))