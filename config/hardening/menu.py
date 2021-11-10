#!/usr/bin/python3
# Graphical Kickstart Script
#
# This script was written by Frank Caviggia, Red Hat Consulting
# Last update was 14 April 2017
# This script is NOT SUPPORTED by Red Hat Global Support Services.
#
# Author: Frank Caviggia (fcaviggia@gmail.com)
# Copyright: Red Hat, (C) 2014
# License: Apache License, Version 2.0


# Possibly replace pygtk,gtk with gtk+ and version verificaiton?
#    import pygtk,gtk
import os,sys,re,crypt,random,gi
try:
    os.environ['DISPLAY']
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk;
    from gi.repository import Gdk;
except:
    print("Error: DISPLAY environment varible not set.")
    sys.exit(1)

# Class containing verification items
class Verification:
    # Name/Comment Check
    def check_name(self,name):
        pattern = re.compile(r"^[ a-zA-Z']+$",re.VERBOSE)
        if re.match(pattern,name):
            return True
        else:
            return False

    # Check for valid Unix username
    def check_username(self,username):
        pattern = re.compile(r"^\w{5,255}$",re.VERBOSE)
        if re.match(pattern,username):
            return True
        else:
            return False

    # Check for valid Unix UID
    def check_uid(self,uid):
        pattern = re.compile(r"^\d{1,10}$",re.VERBOSE)
        if re.match(pattern,uid):
            return True
        else:
            return False

    # Check for valid IP address
    def check_ip(self,ip):
        pattern = re.compile(r"\b(([01]?\d?\d|2[0-4]\d|25[0-5])\.){3}([01]?\d?\d|2[0-4]\d|25[0-5])\b",re.VERBOSE)
        if re.match(pattern,ip) and ip != "0.0.0.0":
            return True
        else:
            return False

    # Check for valid system hostanme
    def check_hostname(self,hostname):
        pattern = re.compile(r"^[a-zA-Z0-9\-\.]{1,100}$",re.VERBOSE)
        if re.match(pattern,hostname):
            return True
        else:
            return False


# Display Menu
class Display_Menu:
    def __init__(self):

        # Initialize Additional Configuration Files
        f = open('/tmp/hardening-post','w')
        f.write('')
        #f.close()
        f = open('/tmp/hardening-packages','w')
        f.write('')
        #f.close()
    
        # Data Storage
        self.data = {}
    
        # Verification Functions
        self.verify = Verification()
    
        # Create Main Window
        self.window = Gtk.Window()
        self.window.set_title("Red Hat Enterprise Linux 8 - SSG Installation Menu")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete_event",Gtk.main_quit)
        self.display = Gdk.Display.get_default()
        self.screen = self.display.get_default_screen()
        self.hres = self.screen.get_width()
        self.vres = self.screen.get_height()
        self.window.connect("key-release-event",self.event_key)

        # Create Main Vertical Box to Populate
        self.vbox = Gtk.VBox()

        if self.hres == 640:
            self.window.resize(640,480)
        elif self.hres > 640:
            self.window.resize(800,600)
            # RedHat Logo
            self.logo = Gtk.Image()
            self.logo.set_from_file("/run/install/repo/hardening/top.png")
            self.logo.set_alignment(0,0)
            self.logo.set_padding(0,0)
            self.vbox.add(self.logo)

        # Creates Header
        self.header = Gtk.HBox()
        self.label = Gtk.Label("<span font_family='liberation-sans' weight='bold' foreground='red' size='large'>  Red Hat Enterprise Linux 8 - SCAP Security Guide Installation  </span>")
        self.label.set_use_markup(True)
        self.header.add(self.label)
        self.vbox.add(self.header)

        # Creates Information Message
        self.label = Gtk.Label('This DVD installs Red Hat Enterprise Linux 8 with configurations required by multiple government regulations')
        self.vbox.add(self.label)
        self.label = Gtk.Label('using the SCAP Security Guide (SSG) as a hardening script.                  RHEL 8 (SSG DVD Installer v.0.8b)')
        self.vbox.add(self.label)

        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)    

        # System Configuration
        self.system = Gtk.HBox()
        self.label = Gtk.Label("   Hostname: ")
        self.system.pack_start(self.label,False,True, 0)
        self.hostname = Gtk.Entry()
        self.hostname.set_size_request(225,-1)
        self.system.pack_start(self.hostname,False,True,0)
        try:
            if os.environ['HOSTNAME'] != '':
                self.hostname.set_text(os.environ['HOSTNAME'])
            else:
                self.hostname.set_text('localhost.localdomain')
        except:
            self.hostname.set_text('localhost.localdomain')
        self.label = Gtk.Label("              System Profile: ") 
        self.system.pack_start(self.label,False,True, 0)
        self.system_profile = Gtk.ComboBoxText()  
        self.system_profile.append_text("Minimal Installation")
        self.system_profile.append_text("IdM Authentication Server")
        self.system_profile.append_text("RHEV-Attached KVM Server")
        self.system_profile.append_text("User Workstation")
        self.system_profile.append_text("Standalone KVM Server")
        self.system_profile.set_active(0)
        self.system_profile.connect('changed',self.configure_system_profile)
        self.system.pack_start(self.system_profile,False,True,0)
        self.vbox.add(self.system)

        self.classification = Gtk.HBox()
        self.label = Gtk.Label("                                                                               System Classification: ")
        self.classification.pack_start(self.label,False,True, 0)
        self.system_classification = Gtk.ComboBoxText()
        self.system_classification.append_text("UNCLASSIFIED")
        self.system_classification.append_text("UNCLASSIFIED//FOUO")
        self.system_classification.append_text("CONFIDENTIAL")
        self.system_classification.append_text("SECRET")
        self.system_classification.append_text("TOP SECRET")
        self.system_classification.append_text("TOP SECRET//SCI")
        self.system_classification.append_text("TOP SECRET//SCI//NOFORN")
        self.system_classification.set_active(0)
        self.classification.pack_start(self.system_classification,False,True,0)
        self.vbox.add(self.classification)

        self.security = Gtk.HBox()
        self.label = Gtk.Label("                                                                     SCAP Security Guide Profile: ")
        self.security.pack_start(self.label,False,True, 0)
        self.system_security = Gtk.ComboBoxText()
        self.system_security.append_text("DISA STIG")
        self.system_security.set_active(0)
        self.system_security.connect('changed',self.configure_system_profile)
        self.security.pack_start(self.system_security,False,True,0)
        self.vbox.add(self.security)

        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)


        # System Information
        self.cpu_cores = 0
        self.cpu_model = ''
        self.cpu_arch = ''
        self.system_memory = {}
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('model name'):
                        self.cpu_model = line.rstrip('\n').split(':')[1]
                        self.cpu_cores += 1
                    elif line.rstrip('\n').startswith('flags') or line.rstrip('\n').startswith('Features'):
                        if 'lm' in line.rstrip('\n').split():
                            self.cpu_arch = '64-bit'
                        else:
                            self.cpu_arch = '32-bit'
        f.close()

        with open('/proc/meminfo') as f:
            for line in f:
                self.system_memory[line.split(':')[0]] = line.split(':')[1].strip()
        f.close()
                        
        self.cpu_information = Gtk.HBox()
        self.label = Gtk.Label("   CPU Model: ")
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label(" %s "%(self.cpu_model))
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label("   CPU Threads: ")
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label(" %d "%(self.cpu_cores))
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label("   Architecure: ")
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label(" %s "%(self.cpu_arch))
        self.cpu_information.pack_start(self.label,False,True, 0)
        self.vbox.add(self.cpu_information)

        self.memory_information = Gtk.HBox()
        self.label = Gtk.Label("   Total System Memory: ")
        self.memory_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label(" %s "%(self.system_memory['MemTotal']))
        self.memory_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label("   Free Memory: ")
        self.memory_information.pack_start(self.label,False,True, 0)
        self.label = Gtk.Label(" %s "%(self.system_memory['MemFree']))
        self.memory_information.pack_start(self.label,False,True, 0)
        self.vbox.add(self.memory_information)

        # Disk Partitioning Section
        self.label = Gtk.Label("\n<span font_family='liberation-sans' weight='bold'>Disk Partitioning</span>")
        self.label.set_use_markup(True)
        self.vbox.add(self.label)

        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)

        # List Disks
        self.disk_list = Gtk.HBox()

        self.disk_info = []
        self.disk_total = 0
        self.output = os.popen('list-harddrives')
        for self.line in self.output:
            self.line = self.line.strip()
            if not ('fd0' in self.line or 'sr0' in self.line):
                self.disk_info.append(self.line.split(' '))
               
        self.label = Gtk.Label("   Available Disks: ")
        self.disk_list.pack_start(self.label, False, True, 0)

        if len(self.disk_info) == 0:
            self.label = Gtk.Label("No Drives Available.")
            self.disk_list.pack_start(self.label,False,True,0)
        else:
            for i in range(len(self.disk_info)):
                if len(self.disk_info) > 5:
                    exec("self.disk%d = Gtk.CheckButton(self.disk_info[%d][0])"%(i,i))
                else:
                    exec("self.disk%s = Gtk.CheckButton(self.disk_info[%d][0] +' ('+ str(int(float(self.disk_info[%d][1]))/1024) +'Gb)')"%(i,i,i))
                exec("self.disk%d.set_active(True)"%(i))
                exec("self.disk_list.pack_start(self.disk%d, False, True, 0)"%(i))
                self.disk_total += int(float(self.disk_info[i][1])/1024)

        self.vbox.add(self.disk_list)

        # Disk Encryption (Ability to disable LUKS for self encrypting drives)
        self.encrypt = Gtk.HBox()

        self.label = Gtk.Label("                             ")
        self.encrypt.pack_start(self.label, False, True, 0)

        self.encrypt_disk = Gtk.CheckButton('Encrypt Drives with LUKS')
        self.encrypt_disk.set_active(True)
        self.encrypt.pack_start(self.encrypt_disk, False, True, 0)

        self.label = Gtk.Label("   ")
        self.encrypt.pack_start(self.label, False, True, 0)

        self.fips_kernel = Gtk.CheckButton('Kernel in FIPS 140-2 Mode')
        self.fips_kernel.set_active(True)
        self.encrypt.pack_start(self.fips_kernel, False, True, 0)

        self.nousb_kernel = Gtk.CheckButton('Disable USB (nousb)')
        self.nousb_kernel.set_active(False)
        self.encrypt.pack_start(self.nousb_kernel, False, True, 0)

        self.vbox.add(self.encrypt)


        # Minimal Installation Warning
        if self.disk_total < 8:
            self.MessageBox(self.window,"<b>Recommended minimum of 8Gb disk space for a Minimal Install!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)

        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)

        # Partitioning
        self.label = Gtk.Label('Required LVM Partitioning Percentage')
        self.vbox.add(self.label)
        self.partitioning1 = Gtk.HBox()
        self.label = Gtk.Label("           ROOT (/) ")
        self.partitioning1.pack_start(self.label,False,True,0)
        self.root_range = Gtk.Adjustment(30,1,95,1,0, 0)
        self.root_partition = Gtk.SpinButton(adjustment=self.root_range,climb_rate=1,digits=0)
        self.root_partition.connect('value-changed',self.lvm_check)
        self.partitioning1.pack_start(self.root_partition,False,True,0)
        self.label = Gtk.Label("%  HOME (/home) ")
        self.partitioning1.pack_start(self.label,False,True,0)
        self.home_range = Gtk.Adjustment(25,1,95,1,0, 0)
        self.home_partition = Gtk.SpinButton(adjustment=self.home_range,climb_rate=1,digits=0)
        self.home_partition.connect('value-changed',self.lvm_check)
        self.partitioning1.pack_start(self.home_partition,False,True,0)
        self.label = Gtk.Label("%  TMP (/tmp) ")
        self.partitioning1.pack_start(self.label,False,True,0)
        self.tmp_range = Gtk.Adjustment(10,1,60,1,0, 0)
        self.tmp_partition = Gtk.SpinButton(adjustment=self.tmp_range,climb_rate=1,digits=0)
        self.tmp_partition.connect('value-changed',self.lvm_check)
        self.partitioning1.pack_start(self.tmp_partition,False,True,0)
        self.label = Gtk.Label("%  VAR (/var) ")
        self.partitioning1.pack_start(self.label,False,True,0)
        self.var_range = Gtk.Adjustment(10,1,95,1,0, 0)
        self.var_partition = Gtk.SpinButton(adjustment=self.var_range,climb_rate=1,digits=0)
        self.var_partition.connect('value-changed',self.lvm_check)
        self.partitioning1.pack_start(self.var_partition,False,True,0)
        self.label = Gtk.Label("%")
        self.partitioning1.pack_start(self.label,False,True,0)

        self.vbox.add(self.partitioning1)
        self.partitioning2 = Gtk.HBox()
        self.label = Gtk.Label("  LOG (/var/log) ")
        self.partitioning2.pack_start(self.label,False,True,0)
        self.log_range = Gtk.Adjustment(10,1,75,1,0, 0)
        self.log_partition = Gtk.SpinButton(adjustment=self.log_range,climb_rate=1,digits=0)
        self.log_partition.connect('value-changed',self.lvm_check)
        self.partitioning2.pack_start(self.log_partition,False,True,0)
        self.label = Gtk.Label("%  AUDIT (/var/log/audit) ")
        self.partitioning2.pack_start(self.label,False,True,0)
        self.audit_range = Gtk.Adjustment(10,1,75,1,0, 0)
        self.audit_partition = Gtk.SpinButton(adjustment=self.audit_range,climb_rate=1,digits=0)
        self.audit_partition.connect('value-changed',self.lvm_check)
        self.partitioning2.pack_start(self.audit_partition,False,True,0)
        self.label = Gtk.Label("%  SWAP ")
        self.partitioning2.pack_start(self.label,False,True,0)
        self.swap_range = Gtk.Adjustment(5,1,25,1,0, 0)
        self.swap_partition = Gtk.SpinButton(adjustment=self.swap_range,climb_rate=1,digits=0)
        self.swap_partition.connect('value-changed',self.lvm_check)
        self.partitioning2.pack_start(self.swap_partition,False,True,0)
        self.label = Gtk.Label("%")
        self.partitioning2.pack_start(self.label,False,True,0)
        self.vbox.add(self.partitioning2)
        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)
        self.label = Gtk.Label('Optional LVM Partitioning Percentage')
        self.vbox.add(self.label)
        self.partitioning3 = Gtk.HBox()
        self.label = Gtk.Label("           WWW (/var/www) ")
        self.partitioning3.pack_start(self.label,False,True,0)
        self.www_range = Gtk.Adjustment(0,0,90,1,0, 0)
        self.www_partition = Gtk.SpinButton(adjustment=self.www_range,climb_rate=1,digits=0)
        self.www_partition.connect('value-changed',self.lvm_check)
        self.partitioning3.pack_start(self.www_partition,False,True,0)
        self.label = Gtk.Label("%   OPT (/opt) ")
        self.partitioning3.pack_start(self.label,False,True,0)
        self.opt_range = Gtk.Adjustment(0,0,90,1,0, 0)
        self.opt_partition = Gtk.SpinButton(adjustment=self.opt_range,climb_rate=1,digits=0)
        self.opt_partition.connect('value-changed',self.lvm_check)
        self.partitioning3.pack_start(self.opt_partition,False,True,0)
        self.label = Gtk.Label("%")
        self.partitioning3.pack_start(self.label,False,True,0)
        self.vbox.add(self.partitioning3)

        # Blank Label
        self.label = Gtk.Label("")
        self.vbox.add(self.label)

        self.partition_message = Gtk.HBox()
        self.label = Gtk.Label('    Note: LVM Partitions should add up to 100% or less before proceeding.     <b>Currently Used:</b> ')
        self.label.set_use_markup(True)
        self.partition_message.pack_start(self.label,False,True,0)
        self.partition_used = Gtk.Label('100%')
        self.partition_message.pack_start(self.partition_used,False,True,0)
        self.vbox.add(self.partition_message)

        # Button Bar at the Bottom of the Window
        self.label = Gtk.Label("")
        self.vbox.add(self.label)
        self.button_bar = Gtk.HBox()

        # Apply Configurations
        self.button1 = Gtk.Button("Ok",None)
        self.button1.connect("clicked",self.apply_configuration)
        self.button_bar.pack_end(self.button1,False,True,0)

        # Help
        self.button2 = Gtk.Button("Help",None)
        self.button2.connect("clicked",self.show_help_main)
        self.button_bar.pack_end(self.button2,False,True,0)

        # Network Configuration
        self.button3 = Gtk.Button("Network",None)
        self.button3.connect("clicked",self.configure_network,self.window)
        self.button_bar.pack_end(self.button3,False,True,0)

        # Network Configuration Default Values
        self.network_device = 0
        self.network_dhcp = True
        self.network_ip = "192.168.0.2"
        self.network_netmask = "255.255.255.0"
        self.network_gateway = "192.168.0.1"
        self.network_dns1 = "8.8.8.8"
        self.network_dns2 = "8.8.4.4"

        self.vbox.add(self.button_bar)
        self.window.add(self.vbox)
        self.window.show_all()

        ## STOCK CONFIGURATIONS (Minimal Install)
        # Default SSG Profile (DISA STIG)
        self.profile='stig'
        # Post Configuration (nochroot)
        f = open('/tmp/hardening-post-nochroot','w')
        f.write('')
        f.close()
        # Post Configuration
        f = open('/tmp/hardening-post','w')
        # Run Hardening Script
        f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
        # Firewall Configuration
        f.write('firewall-cmd --permanent --add-service=ssh\n')
        f.write('firewall-cmd --reload\n')
        f.close()
        # Package Selection
        f = open('/tmp/hardening-packages','w')
        f.write('')
        f.close()

    # Key Press Event
    def event_key(self,args,event):
        if event.keyval == Gdk.keyval_from_name("F12"): 
            self.apply_configuration(args)
        elif event.keyval == Gdk.keyval_from_name("F1"):
            self.show_help_main(args)

    # Shows Help for Main Install
    def show_help_main(self,args):
        self.help_text = ("<b>Install Help</b>\n\n- All LVM partitions need to take less than or equal to 100% of the LVM Volume Group.\n\n- Pressing OK prompts for a password to encrypt Disk (LUKS), GRUB, and admin password.\n\n- The sshusers group controls remote access, wheel group is for root users, and isso group is for limited root with auditing permissions.\n\n- To access root remotely via ssh you need to create a user and add them to the wheel and sshusers groups.\n\n- Minimum password length is 15 characters, using a strong password is recommended.\n")
        self.MessageBox(self.window,self.help_text,Gtk.MessageType.INFO)


    # System Profile Configuration
    def configure_system_profile(self,args):

        # Turn on FIPS 140-2 mode for Kernel (Default)
        self.fips_kernel.set_active(True)

        # Zero out partitioning values
        self.opt_partition.set_value(0)
        self.www_partition.set_value(0)
        self.swap_partition.set_value(0)
        self.tmp_partition.set_value(0)
        self.var_partition.set_value(0)
        self.log_partition.set_value(0)
        self.audit_partition.set_value(0)
        self.home_partition.set_value(0)
        self.root_partition.set_value(0)

        # Define SSG Security Profile
        if int(self.system_security.get_active()) == 0:
            self.profile='stig'

        ################################################################################################################
        # Minimal (Defaults to Kickstart)
        ################################################################################################################
        if int(self.system_profile.get_active()) == 0:
            # Partitioning
            if self.disk_total < 8:
                self.MessageBox(self.window,"<b>Recommended minimum of 8Gb disk space for a Minimal Install!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)
            self.opt_partition.set_value(0)
            self.www_partition.set_value(0)
            self.swap_partition.set_value(5)
            self.tmp_partition.set_value(10)
            self.var_partition.set_value(10)
            self.log_partition.set_value(10)
            self.audit_partition.set_value(10)
            self.home_partition.set_value(25)
            self.root_partition.set_value(30)
            # Post Configuration (nochroot)
            f = open('/tmp/hardening-post-nochroot','w')
            f.write('')
            f.close()
            # Post Configuration
            f = open('/tmp/hardening-post','w')
            # Run Hardening Script
            f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
            # Firewall Configuration
            f.write('firewall-cmd --permanent --add-service=ssh\n')
            f.write('firewall-cmd --reload\n')
            # Runlevel Configuration
            f.write('systemctl set-default multi-user.target\n')
            f.close()
            # Package Selection
            f = open('/tmp/hardening-packages','w')
            f.write('')
            f.close()


        ################################################################################################################
        # IdM/IPA Authentication Server
        ################################################################################################################
        if int(self.system_profile.get_active()) == 1:
            # Partitioning
            if self.disk_total < 10:
                self.MessageBox(self.window,"<b>Recommended minimum of 10Gb disk space for a IdM Authentication Server Install!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)
            self.opt_partition.set_value(0)
            self.www_partition.set_value(5)
            self.swap_partition.set_value(5)
            self.tmp_partition.set_value(10)
            self.var_partition.set_value(10)
            self.log_partition.set_value(10)
            self.audit_partition.set_value(10)
            self.home_partition.set_value(15)
            self.root_partition.set_value(35)
            # Post Configuration (nochroot)
            f = open('/tmp/hardening-post-nochroot','w')
            f.write('')
            f.close()
            # Post Configuration
            f = open('/tmp/hardening-post','w')
            # Run Hardening Script
            f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
            # Firewall Configuration
            f.write('firewall-cmd --permanent --add-service=ssh --add-service=http --add-service=https --add-service=ldap --add-service=ldaps --add-service=kerberos --add-service=kpasswd --add-service=dns --add-service=ntp\n')
            f.write('firewall-cmd --reload\n')
            # Runlevel Configuration
            f.write('systemctl set-default multi-user.target\n')
            f.close()
            # Package Selection
            f = open('/tmp/hardening-packages','w')
            f.write('ipa-server\n')
            f.write('ipa-admintools\n')
            f.write('ipa-client\n')
            f.write('ipa-server-dns\n')
            f.close()
            
        ################################################################################################################
        # RHEV-Attached KVM Server
        ################################################################################################################
        if int(self.system_profile.get_active()) == 2:
            # WARNING - HARDENING SCRIPT NOT RUN!
            self.MessageBox(self.window,"<b>Warning:</b> Please run the following script before adding system RHEV-M:\n\n   # /root/rhevm-preinstall.sh\n\nAfter adding the system to RHEV-M, run the following:\n\n   # /root/rhevm-postinstall.sh",Gtk.MessageType.WARNING)
            # Partitioning
            if self.disk_total < 60:
                self.MessageBox(self.window,"<b>Recommended minimum of 60Gb disk space for a RHEV-Attached KVM Server Install!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)
            self.opt_partition.set_value(0)
            self.www_partition.set_value(0)
            self.swap_partition.set_value(5)
            self.tmp_partition.set_value(10)
            self.var_partition.set_value(10)
            self.log_partition.set_value(10)
            self.audit_partition.set_value(10)
            self.home_partition.set_value(25)
            self.root_partition.set_value(30)
            # Post Configuration (nochroot)
            f = open('/tmp/hardening-post-nochroot','w')
            f.write('')
            f.close()
            # Post Configuration
            f = open('/tmp/hardening-post','w')
            # Run Hardening Script
            f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
            # RHEV Scripts for Pre-Install/Post-Install
            f.write('cp /root/hardening/rhevm*.sh /root/\n')
            # Firewall Configuration
            f.write('cp /root/hardening/iptables.sh /root/\n')
            f.write('cp /root/hardening/firewalld.sh /root/\n')
            f.write('/root/firewalld.sh --kvm\n')
            # Runlevel Configuration
            f.write('systemctl set-default multi-user.target\n')
            f.close()
            # Package Selection
            f = open('/tmp/hardening-packages','w')
            f.write('-firewall*\n')
            f.write('ebtables\n')
            f.write('iptables\n')
            f.write('libvirt\n')
            f.write('pciutils\n')
            f.close()


        ################################################################################################################
        # User Workstation
        ################################################################################################################
        if int(self.system_profile.get_active()) == 3:
            # Partitioning
            if self.disk_total < 12:
                self.MessageBox(self.window,"<b>Recommended minimum 12Gb disk space for a User Workstation!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)
            self.opt_partition.set_value(0)
            self.www_partition.set_value(0)
            self.swap_partition.set_value(5)
            self.tmp_partition.set_value(10)
            self.var_partition.set_value(10)
            self.log_partition.set_value(10)
            self.audit_partition.set_value(10)
            self.home_partition.set_value(25)
            self.root_partition.set_value(30)
            # Post Configuration (nochroot)
            f = open('/tmp/hardening-post-nochroot','w')
            f.write('')
            f.close()
            # Post Configuration
            f = open('/tmp/hardening-post','w')
            # Run Hardening Script
            f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
            f.write('/usr/bin/oscap xccdf eval --profile stig-firefox-upstream --remediate --results /root/`hostname`-ssg-firefox-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-firefox-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-firefox-xccdf.xml\n')
            # Firewall Configuration
            f.write('firewall-cmd --permanent --add-service=ssh\n')
            f.write('firewall-cmd --reload\n')
            # Runlevel Configuration
            f.write('systemctl set-default graphical.target\n')
            f.close()
            # Package Selection
            f = open('/tmp/hardening-packages','w')
            f.write('@x-window-system\n')
            f.write('liberation*\n')
            f.write('dejavu*\n')
            f.write('firewall-config\n')
            f.write('gnome-classic-session\n')
            f.write('gnome-terminal\n')
            f.write('gnome-calculator\n')
            f.write('control-center\n')
            f.write('pulseaudio-module-x11\n')
            f.write('alsa-plugins-pulseaudio\n')
            f.write('seahorse\n')
            f.write('seahorse-nautilus\n')
            f.write('file-roller\n')
            f.write('file-roller-nautilus\n')
            f.write('evince\n')
            f.write('evince-nautilus\n')
            f.write('firefox\n')
            f.write('pygtk2\n')
            f.write('vim-X11\n')
            f.close()


        ################################################################################################################
        # Standalone KVM Installation
        ################################################################################################################
        if int(self.system_profile.get_active()) == 4:
            # Partitioning
            if self.disk_total < 60:
                self.MessageBox(self.window,"<b>Recommended minimum 60Gb disk space for a RHEL/KVM Server!</b>\n\n You have "+str(self.disk_total)+"Gb available.",Gtk.MessageType.WARNING)
                self.opt_partition.set_value(0)
                self.www_partition.set_value(0)
                self.swap_partition.set_value(2)
                self.tmp_partition.set_value(3)
                self.var_partition.set_value(65)
                self.log_partition.set_value(5)
                self.audit_partition.set_value(5)
                self.home_partition.set_value(5)
                self.root_partition.set_value(15)
            # Post Configuration (nochroot)
            f = open('/tmp/hardening-post-nochroot','w')
            f.write('')
            f.close()
            # Post Configuration
            f = open('/tmp/hardening-post','w')
            # Run Hardening Script
            f.write('/usr/bin/oscap xccdf eval --profile '+str(self.profile)+' --remediate --results /root/`hostname`-ssg-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-rhel8-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-xccdf.xml\n')
            f.write('/usr/bin/oscap xccdf eval --profile stig-firefox-upstream --remediate --results /root/`hostname`-ssg-firefox-results.xml  --cpe /usr/share/xml/scap/ssg/content/ssg-firefox-cpe-dictionary.xml /usr/share/xml/scap/ssg/content/ssg-firefox-xccdf.xml\n')
            # Firewall Configuration
            f.write('cp /root/hardening/iptables.sh /root/\n')
            f.write('cp /root/hardening/firewalld.sh /root/\n')
            f.write('/root/firewalld.sh --kvm\n')
            # Runlevel Configuration
            f.write('systemctl set-default graphical.target\n')
            f.close()
            # Package Selection
            f = open('/tmp/hardening-packages','w')
            f.write('@x-window-system\n')
            f.write('@virtualization-client\n')
            f.write('@virtualization-platform\n')
            f.write('liberation*\n')
            f.write('dejavu*\n')
            f.write('gnome-classic-session\n')
            f.write('gnome-terminal\n')
            f.write('gnome-calculator\n')
            f.write('control-center\n')
            f.write('pulseaudio-module-x11\n')
            f.write('alsa-plugins-pulseaudio\n')
            f.write('seahorse\n')
            f.write('seahorse-nautilus\n')
            f.write('file-roller\n')
            f.write('file-roller-nautilus\n')
            f.write('evince\n')
            f.write('evince-nautilus\n')
            f.write('firefox\n')
            f.write('pygtk2\n')
            f.write('vim-X11\n')
            # Remove FirewallD and Network Manager (virt-manager will define networks)
            f.write('-firewall*\n')
            f.write('-NetworkManager*\n')
            f.write('ebtables\n')
            f.write('iptables\n')
            f.close()


    # Check LVM Partitioning
    def lvm_check(self,args):
        self.lvm = self.root_partition.get_value_as_int()+self.home_partition.get_value_as_int()+self.tmp_partition.get_value_as_int()+self.var_partition.get_value_as_int()+self.log_partition.get_value_as_int()+self.audit_partition.get_value_as_int()+self.swap_partition.get_value_as_int()+self.www_partition.get_value_as_int()+self.opt_partition.get_value_as_int()
        self.partition_used.set_label(str(self.lvm)+'%')
        if int(self.lvm) > 100:
            self.MessageBox(self.window,"<b>Verify that LVM configuration is not over 100%!</b>",Gtk.MessageType.ERROR)
            return False
        else:
            return True


    # Display Message Box (e.g. Help Screen, Warning Screen, etc.)
    def MessageBox(self,parent,text,type=Gtk.MessageType.INFO):
        message = Gtk.MessageDialog(parent,0,type,Gtk.ButtonsType.OK)
        message.set_markup(text)    
        response = message.run()
        if response == Gtk.ResponseType.OK:
            message.destroy()

        
    # Get Password
    def get_password(self,parent):
        dialog = Gtk.Dialog("Configure System Password",parent,Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL,Gtk.ResponseType.REJECT,Gtk.STOCK_OK,Gtk.ResponseType.ACCEPT))
        self.pass1 = Gtk.HBox()
        self.label1 = Gtk.Label("           Password: ")
        self.pass1.pack_start(self.label1,False,True,0)
        self.password1 = Gtk.Entry()
        self.password1.set_visibility(False)
        self.pass1.pack_start(self.password1,False,True,0)
        dialog.vbox.add(self.pass1)
        self.pass2 = Gtk.HBox()
        self.label2 = Gtk.Label("  Verify Password: ")
        self.pass2.pack_start(self.label2,False,True,0)
        self.password2 = Gtk.Entry()
        self.password2.set_visibility(False)
        self.pass2.pack_start(self.password2,False,True,0)
        dialog.vbox.add(self.pass2)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.a = self.password1.get_text()
            self.b = self.password2.get_text()
            dialog.destroy()
        else:
            self.a = ''
            self.b = ''
            dialog.destroy()


    # Configure Network Dialog
    def configure_network(self,parent,window):
        self.network_dialog = Gtk.Dialog("Configure Network",window,Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK,Gtk.ResponseType.ACCEPT))

        # List Network Ports
        self.network = Gtk.HBox()
        self.label = Gtk.Label(" Network Device(s): ")
        self.network.pack_start(self.label, False, True, 0)
        self.network_devices = Gtk.combo_box_new_text()
        self.output = os.popen("ip link show | grep UP | awk -F ': ' '{ print $2 }'")
        for self.line in self.output:
            self.line = self.line.strip()
            if not ('lo' in self.line):
                self.network_devices.append_text(self.line)
        self.network.pack_start(self.network_devices,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.dhcp = Gtk.CheckButton('DHCP')
        self.network.pack_start(self.dhcp,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.label = Gtk.Label("           IP Address: ")
        self.network.pack_start(self.label,False,True,0)
        self.ip = Gtk.Entry()
        self.network.pack_start(self.ip,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.label = Gtk.Label("             Netmask: ")
        self.network.pack_start(self.label,False,True,0)
        self.netmask = Gtk.Entry()
        self.network.pack_start(self.netmask,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.label = Gtk.Label("               Gateway: ")
        self.network.pack_start(self.label,False,True,0)
        self.gateway = Gtk.Entry()
        self.network.pack_start(self.gateway,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.label = Gtk.Label("                   DNS1: ")
        self.network.pack_start(self.label,False,True,0)
        self.dns1 = Gtk.Entry()
        self.network.pack_start(self.dns1,False,True,0)
        self.network_dialog.vbox.add(self.network)
        self.network = Gtk.HBox()
        self.label = Gtk.Label("                   DNS2: ")
        self.network.pack_start(self.label,False,True,0)
        self.dns2 = Gtk.Entry()
        self.network.pack_start(self.dns2,False,True,0)
        self.network_dialog.vbox.add(self.network)

        self.dhcp.set_active(self.network_dhcp)
        self.ip.set_text(self.network_ip)
        self.netmask.set_text(self.network_netmask)
        self.gateway.set_text(self.network_gateway)
        self.dns1.set_text(self.network_dns1)
        self.dns2.set_text(self.network_dns2)
        self.network_devices.set_active(self.network_device)

        if self.dhcp.get_active() == True:
            self.dhcp.set_label("DHCP")
            self.ip.set_sensitive(False)
            self.netmask.set_sensitive(False)
            self.gateway.set_sensitive(False)
            self.dns1.set_sensitive(False)
            self.dns2.set_sensitive(False)
        else:
            self.dhcp.set_label("Static IP")
            self.ip.set_sensitive(True)
            self.netmask.set_sensitive(True)
            self.gateway.set_sensitive(True)
            self.dns1.set_sensitive(True)
            self.dns2.set_sensitive(True)

        self.dhcp.connect("toggled", self.check_network)
        self.ip.connect("grab-focus", self.check_network)
        self.netmask.connect("grab-focus", self.check_network)
        self.gateway.connect("grab-focus", self.check_network)
        self.dns1.connect("grab-focus", self.check_network)
        self.dns2.connect("grab-focus", self.check_network)
        self.network_dialog.connect("move-focus", self.check_network)

        self.network_dialog.show_all()
        response = self.network_dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.network_device = self.network_devices.get_active()
            self.network_name = self.network_devices.get_active_text()
            self.network_dhcp = self.dhcp.get_active()
            self.network_ip = self.ip.get_text()
            self.network_netmask = self.netmask.get_text()
            self.network_gateway = self.gateway.get_text()
            self.network_dns1 = self.dns1.get_text()
            self.network_dns2 = self.dns2.get_text()
            
            # Write Network Configuration File
            if self.dhcp.get_active() == True:          
                f = open('/tmp/networking','w')
                f.write('network --bootproto=dhcp --device='+str(self.network_name)+' --noipv6 --activate\n')
                f.close()
            else:
                f = open('/tmp/networking','w')
                f.write('network --bootproto=static --ip='+str(self.network_ip)+' --netmask='+str(self.network_netmask)+' --gateway='+str(self.network_gateway)+' --nameserver '+str(self.network_dns1)+','+str(self.network_dns2)+' --device='+str(self.network_name)+' --noipv6 --activate\n')
                f.close()

            self.network_dialog.destroy()
                

    # DHCP Button Toggle
    def check_network(self,widget,event=None):

        self.network_error = 0

        if self.dhcp.get_active() == True:
            self.dhcp.set_label("DHCP")
            self.ip.set_sensitive(False)
            self.netmask.set_sensitive(False)
            self.gateway.set_sensitive(False)
            self.dns1.set_sensitive(False)
            self.dns2.set_sensitive(False)
        else:
            self.dhcp.set_label("Static IP")
            self.ip.set_sensitive(True)
            self.netmask.set_sensitive(True)
            self.gateway.set_sensitive(True)
            self.dns1.set_sensitive(True)
            self.dns2.set_sensitive(True)

            if self.verify.check_ip(self.ip.get_text()) == False:
                self.MessageBox(self.window,"<b>Invalid IP Address!</b>",Gtk.MessageType.ERROR)
                self.network_error = 1
            if self.verify.check_ip(self.netmask.get_text()) == False:
                self.MessageBox(self.window,"<b>Invalid Netmask!</b>",Gtk.MessageType.ERROR)
                self.network_error = 1
            if self.verify.check_ip(self.gateway.get_text()) == False:
                self.MessageBox(self.window,"<b>Invalid Gateway!</b>",Gtk.MessageType.ERROR)
                self.network_error = 1
            if self.verify.check_ip(self.dns1.get_text()) == False:
                self.MessageBox(self.window,"<b>Invalid DNS1 Address!</b>",Gtk.MessageType.ERROR)
                self.network_error = 1
            if self.verify.check_ip(self.dns2.get_text()) == False:
                self.MessageBox(self.window,"<b>Invalid DNS2 Address!</b>",Gtk.MessageType.ERROR)
                self.network_error = 1

        if self.network_error == 1:
            self.network_dialog.set_response_sensitive(Gtk.ResponseType.ACCEPT,False)
            return False    
        else:
            self.network_dialog.set_response_sensitive(Gtk.ResponseType.ACCEPT,True)
            return True


    # Apply Configurations to Kickstart File
    def apply_configuration(self,args):

        # FIPS 140-2 Configuration
        if self.fips_kernel.get_active() == True:
            f = open('/tmp/hardening-post','a')
            # Enable FIPS 140-2 mode in Kernel
            f.write('\n/root/hardening/fips-kernel-mode.sh\n')
            #f.close()
        else:
            f = open('/tmp/hardening-post','a')
            # Disable FIPS 140-2 mode in Kernel
            f.write('\ngrubby --update-kernel=ALL --remove-args="fips=1"\n')
            f.write('\n/usr/bin/sed -i "s/ fips=1//" /etc/default/grub\n')
            #f.close()

        # Disable USB (nousb kernel option)
        if self.nousb_kernel.get_active() == True:
            f = open('/tmp/hardening-post','a')
            # Enable nousb mode in Kernel
            f.write('\ngrubby --update-kernel=ALL --args="nousb"\n')
            f.write('\n/usr/bin/sed -i "s/ quiet/quiet nousb/" /etc/default/grub\n')
            #f.close()
        else:
            f = open('/tmp/hardening-post','a')
            # Disable nousb mode in Kernel
            f.write('\ngrubby --update-kernel=ALL --remove-args="nousb"\n')
            f.write('\n/usr/bin/sed -i "s/ nousb//" /etc/default/grub\n')
            #f.close()

        # Set system password
        while True:
            self.get_password(self.window)
            if self.a == self.b:
                if len(self.a) == 0:
                    return
                elif len(self.a) >= 15:
                    self.passwd = self.a
                    break
                else:
                    self.MessageBox(self.window,"<b>Password too short! 15 Characters Required.</b>",Gtk.MessageType.ERROR)
            else:
                self.MessageBox(self.window,"<b>Passwords Don't Match!</b>",Gtk.MessageType.ERROR)
            
        self.error = 0

        if self.verify.check_hostname(self.hostname.get_text()) == False:
            self.MessageBox(self.window,"<b>Invalid Hostname!</b>",Gtk.MessageType.ERROR)
            self.error = 1

        # Check Install Disks   
        self.install_disks = ""
        self.ignore_disks = ""
        for i in range(len(self.disk_info)):
            if eval("self.disk%d.get_active()"%(i)) == True:
                self.install_disks += self.disk_info[i][0]+","
            else:
                self.ignore_disks += self.disk_info[i][0]+","
        self.data["INSTALL_DRIVES"] = self.install_disks[:-1]
        self.data["IGNORE_DRIVES"] = self.ignore_disks[:-1]
        if self.install_disks == "":
            self.MessageBox(self.window,"<b>Please select at least one install disk!</b>",Gtk.MessageType.ERROR)
            self.error = 1

        # Check LVM Partitioning
        if self.lvm_check(args) == False:
            self.error = 1

        # Write Kickstart File
        if self.error == 0:

            # Generate Salt
            self.salt = ''
            self.alphabet = '.abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            for self.i in range(16):
                self.index = random.randrange(len(self.alphabet))
                self.salt = self.salt+self.alphabet[self.index]

            # Encrypt Password
            self.salt = '$6$'+self.salt
            self.password = crypt.crypt(self.passwd,self.salt)

            # Write Classification Banner Settings
            f = open('/tmp/classification-banner','a')
            f.write('message = "'+str(self.system_classification.get_active_text())+'"\n')
            if int(self.system_classification.get_active()) == 0 or int(self.system_classification.get_active()) == 1:
                f.write('fgcolor = "#FFFFFF"\n')
                f.write('bgcolor = "#007A33"\n')
            elif int(self.system_classification.get_active()) == 2:
                f.write('fgcolor = "#FFFFFF"\n')
                f.write('bgcolor = "#0033A0"\n')
            elif int(self.system_classification.get_active()) == 3:
                f.write('fgcolor = "#FFFFFF"\n')
                f.write('bgcolor = "#C8102E"\n')
            elif int(self.system_classification.get_active()) == 4:
                f.write('fgcolor = "#FFFFFF"\n')
                f.write('bgcolor = "#FF671F"\n')
            elif int(self.system_classification.get_active()) == 5:
                f.write('fgcolor = "#FFFFF"\n')
                f.write('bgcolor = "#F7EA48"\n')
            elif int(self.system_classification.get_active()) == 6:
                f.write('fgcolor = "#000000"\n')
                f.write('bgcolor = "#F7EA48"\n')
            else:
                f.write('fgcolor = "#FFFFFF"\n')
            f.write('bgcolor = "#007A33"\n')
            f.close()

            # Write Kickstart Configuration
            f = open('/tmp/hardening','a')
            f.write('network --hostname '+self.hostname.get_text()+'\n')
            f.write('rootpw --iscrypted '+str(self.password)+' --lock\n') 
            f.write('bootloader --location=mbr --driveorder='+str(self.data["INSTALL_DRIVES"])+' --append="crashkernel=auto rhgb quiet audit=1" --password='+str(self.a)+'\n') 
            f.write('user --name=mr.gency --groups=wheel --password='+str(self.password)+' --iscrypted \n') 
            f.close()
            f = open('/tmp/partitioning','w')
            if self.data["IGNORE_DRIVES"] != "":
                f.write('ignoredisk --drives='+str(self.data["IGNORE_DRIVES"])+'\n')
                f.write('zerombr\n')
                f.write('clearpart --all --drives='+str(self.data["INSTALL_DRIVES"])+'\n')
            if self.encrypt_disk.get_active() == True:
                f.write('part pv.01 --grow --size=200 --encrypted --cipher=\'aes-xts-plain64\' --passphrase='+str(self.passwd)+'\n')
            else:
                f.write('part pv.01 --grow --size=200\n')
                f.write('part /boot --fstype=xfs --size=1024\n')
            if os.path.isdir('/sys/firmware/efi'):
                f.write('part /boot/efi --fstype=efi --size=200\n')
                f.write('volgroup vg1 --pesize=4096 pv.01\n')
                f.write('logvol / --fstype=xfs --name=lv_root --vgname=vg1 --percent='+str(self.root_partition.get_value_as_int())+'\n')
                f.write('logvol /home --fstype=xfs --name=lv_home --vgname=vg1 --percent='+str(self.home_partition.get_value_as_int())+'\n')
                f.write('logvol /tmp --fstype=xfs --name=lv_tmp --vgname=vg1 --percent='+str(self.tmp_partition.get_value_as_int())+'\n')
                f.write('logvol /var --fstype=xfs --name=lv_var --vgname=vg1 --percent='+str(self.var_partition.get_value_as_int())+'\n')
                f.write('logvol /var/log --fstype=xfs --name=lv_log --vgname=vg1 --percent='+str(self.log_partition.get_value_as_int())+'\n')
                f.write('logvol /var/log/audit --fstype=xfs --name=lv_audit --vgname=vg1 --percent='+str(self.audit_partition.get_value_as_int())+'\n')
                f.write('logvol swap --fstype=swap --name=lv_swap --vgname=vg1 --maxsize=4096 --percent='+str(self.swap_partition.get_value_as_int())+'\n')
            if self.opt_partition.get_value_as_int() >= 1:
                f.write('logvol /opt --fstype=xfs --name=lv_opt --vgname=vg1 --percent='+str(self.opt_partition.get_value_as_int())+'\n')
            if self.www_partition.get_value_as_int() >= 1:
                f.write('logvol /var/www --fstype=xfs --name=lv_www --vgname=vg1 --percent='+str(self.www_partition.get_value_as_int())+'\n')
            f.close()
            Gtk.main_quit()


# Executes Window Display
if __name__ == "__main__":
    window = Display_Menu()
    Gtk.main()
