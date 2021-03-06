################################################################################
#
# This program is part of the HPMon Zenpack for Zenoss.
# Copyright (C) 2008, 2009, 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""HPScsiPhyDrvMap

HPScsiPhyDrvMap maps the cpqScsiPhyDrvTable to disks objects

$Id: HPScsiPhyDrvMap.py,v 1.4 2011/01/05 19:35:05 egor Exp $"""

__version__ = '$Revision: 1.4 $'[11:-2]

from Products.DataCollector.plugins.CollectorPlugin import GetTableMap
from Products.DataCollector.plugins.DataMaps import MultiArgs
from HPHardDiskMap import HPHardDiskMap

class HPScsiPhyDrvMap(HPHardDiskMap):
    """Map HP/Compaq insight manager DA Hard Disk tables to model."""

    maptype = "HPScsiPhyDrvMap"
    modname = "ZenPacks.community.HPMon.cpqScsiPhyDrv"

    snmpGetTableMaps = (
        GetTableMap('cpqScsiPhyDrvTable',
                    '.1.3.6.1.4.1.232.5.2.4.1.1',
                    {
                        '.4': 'description',
                        '.5': 'FWRev',
                        '.6': 'vendor',
                        '.7': 'size',
                        '.8': 'bay',
                        '.9': 'status',
                        '.30': 'serialNumber',
                        '.38': 'rpm',
                        '.40': 'hotPlug',
                    }
        ),
    )

    diskTypes = {1: 'SCSI',
                }

    def process(self, device, results, log):
        """collect snmp information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        getdata, tabledata = results
        if not device.id in HPHardDiskMap.oms:
            HPHardDiskMap.oms[device.id] = []
        for oid, disk in tabledata.get('cpqScsiPhyDrvTable', {}).iteritems():
            try:
                om = self.objectMap(disk)
                om.snmpindex = oid.strip('.')
                om.id = self.prepId("HardDisk%s"%om.snmpindex).replace('.','_')
                if not getattr(om,'description',''):om.description='Unknown Disk'
                om.setProductKey = MultiArgs(om.description,
                                            om.description.split()[0])
                om.diskType = self.diskTypes.get(getattr(om, 'diskType', 1),
                                                self.diskTypes[1])
                om.rpm = self.rpms.get(getattr(om,'rpm',1), getattr(om,'rpm',1))
                om.size = getattr(om, 'size', 0) * 1048576
            except AttributeError:
                continue
            HPHardDiskMap.oms[device.id].append(om)
        return
