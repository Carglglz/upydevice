import upydevice
import traceback
import xml.etree.ElementTree as ET
from upydevice.SI_units import ble_SI_units_dict, DATA_FMT

CHARS_XML_DIR = "{}/chars_xml".format(upydevice.__path__[0])

CK = ['0x2A7E', '0x2A84', '0x2A7F', '0x2A80', '0x2A5A',
      '0x2A43', '0x2A42', '0x2A06', '0x2A44', '0x2A3F', '0x2AB3', '0x2A81',
      '0x2A82', '0x2A83', '0x2A58', '0x2A59', '0x2A73', '0x2A72', '0x2A01',
      '0x2AA3', '0x2A19', '0x2A1B', '0x2A1A', '0x2A49', '0x2A35', '0x2A9B',
      '0x2A9C', '0x2A38', '0x2AA4', '0x2AA5', '0x2A22', '0x2A32', '0x2A33',
      '0x2B2B', '0x2B2C', '0x2AA8', '0x2AA7', '0x2AAB', '0x2AAA', '0x2AAC',
      '0x2AA9', '0x2B29', '0x2ACE', '0x2A5C', '0x2A5B', '0x2A2B', '0x2A66',
      '0x2A65', '0x2A63', '0x2A64', '0x2A99', '0x2B2A', '0x2A85', '0x2A86',
      '0x2A08', '0x2AED', '0x2A0A', '0x2A09', '0x2A7D', '0x2A7B', '0x2A56',
      '0x2A57', '0x2A0D', '0x2A6C', '0x2A87', '0x2B2D', '0x2B2E', '0x2A0B',
      '0x2A0C', '0x2A88', '0x2A89', '0x2A26', '0x2A8A', '0x2AD9', '0x2ACC',
      '0x2ADA', '0x2A8B', '0x2AB2', '0x2AA6', '0x2A00', '0x2A04', '0x2A02',
      '0x2A03', '0x2A05', '0x2A8C', '0x2A51', '0x2A18', '0x2A34', '0x2A74',
      '0x2A27', '0x2A39', '0x2A8D', '0x2A37', '0x2A7A', '0x2A8E', '0x2A4C',
      '0x2A4A', '0x2A8F', '0x2ABA', '0x2AB9', '0x2AB7', '0x2AB8', '0x2ABB',
      '0x2A6F', '0x2B22', '0x2B25', '0x2B26', '0x2B23', '0x2B28', '0x2B27',
      '0x2B21', '0x2B20', '0x2B24', '0x2A2A', '0x2AD2', '0x2AAD', '0x2A36',
      '0x2A1E', '0x2A77', '0x2AA2', '0x2A90', '0x2AAE', '0x2A6B', '0x2A6A',
      '0x2AB1', '0x2AB', '0x2ABA0F', '0x2A67', '0x2AB5', '0x2AAF', '0x2A2C',
      '0x2AA0', '0x2AA1', '0x2A29', '0x2A91', '0x2A21', '0x2ADB', '0X2ADC',
      '0X2ADD', '0X2ADE', '0x2A24', '0x2A68', '0x2A3E', '0x2A46', '0x2AC5',
      '0x2AC', '0x2ACAC1', '0x2AC', '0x2ACAC2', '0x2AC6', '0x2AC7', '0x2ABE',
      '0x2AC4', '0x2AC0', '0x2ABF', '0x2ABD', '0x2A5F', '0x2A60', '0x2A5E',
      '0x2A50', '0x2A7', '0x2A7A2', '0x2A7A30', '0x2A69', '0x2A6D', '0x2A4E',
      '0x2A6', '0x2A2A78', '0x2B1D', '0x2B1', '0x2B1B1F', '0x2A52', '0x2A1',
      '0x2A1B3', '0x2A1A3', '0x2A2A4', '0x2A1A4B', '0x2AC9', '0x2A92',
      '0x2A40', '0x2A41', '0x2AD1', '0x2A54', '0x2A53', '0x2A55', '0x2A4F',
      '0x2A31', '0x2A3C', '0x2A10', '0x2A5D', '0x2A25', '0x2B3', '0x2B3A3B',
      '0x2A2', '0x2A2A93',
      '0x2AD0', '0x2ACF', '0x2A3D', '0x2AD7', '0x2AD', '0x2ADA47', '0x2AD8',
      '0x2AD6', '0x2AD4', '0x2A48', '0x2A23', '0x2ABC', '0x2A6E', '0x2A1F',
      '0x2A20', '0x2A1C', '0x2A1D', '0x2A94', '0x2A1', '0x2A1A15', '0x2A13',
      '0x2A16', '0x2A17', '0x2A11', '0x2A0E', '0x2AD3', '0x2ACD', '0x2A7',
      '0x2A7A70', '0x2A95', '0x2A07', '0x2AB4', '0x2A45', '0x2AB6', '0x2A9F',
      '0x2A9A', '0x2A76', '0x2A96', '0x2A97', '0x2A98', '0x2A9D', '0x2A9E',
      '0x2A79']

TK = ['Aerobic Heart Rate Lower Limit',
      'Aerobic Heart Rate Upper Limit',
      'Aerobic Threshold',
      'Age',
      'Aggregate',
      'Alert Category ID',
      'Alert Category ID Bit Mask',
      'Alert Level',
      'Alert Notification Control Point',
      'Alert Status',
      'Altitude',
      'Anaerobic Heart Rate Lower Limit',
      'Anaerobic Heart Rate Upper Limit',
      'Anaerobic Threshold',
      'Analog',
      'Analog Output',
      'Apparent Wind Direction',
      'Apparent Wind Speed',
      'Appearance',
      'Barometric Pressure Trend',
      'Battery Level',
      'Battery Level State',
      'Battery Power State',
      'Blood Pressure Feature',
      'Blood Pressure Measurement',
      'Body Composition Feature',
      'Body Composition Measurement',
      'Body Sensor Location',
      'Bond Management Control Point',
      'Bond Management Features',
      'Boot Keyboard Input Report',
      'Boot Keyboard Output Report',
      'Boot Mouse Input Report',
      'BSS Control Point',
      'BSS Response',
      'CGM Feature',
      'CGM Measurement',
      'CGM Session Run Time',
      'CGM Session Start Time',
      'CGM Specific Ops Control Point',
      'CGM Status',
      'Client Supported Features',
      'Cross Trainer Data',
      'CSC Feature',
      'CSC Measurement',
      'Current Time',
      'Cycling Power Control Point',
      'Cycling Power Feature',
      'Cycling Power Measurement',
      'Cycling Power Vector',
      'Database Change Increment',
      'Database Hash',
      'Date of Birth',
      'Date of Threshold Assessment',
      'Date Time',
      'Date UTC',
      'Day Date Time',
      'Day of Week',
      'Descriptor Value Changed',
      'Dew Point',
      'Digital',
      'Digital Output',
      'DST Offset',
      'Elevation',
      'Email Address',
      'Emergency ID',
      'Emergency Text',
      'Exact Time 100',
      'Exact Time 256',
      'Fat Burn Heart Rate Lower Limit',
      'Fat Burn Heart Rate Upper Limit',
      'Firmware Revision String',
      'First Name',
      'Fitness Machine Control Point',
      'Fitness Machine Feature',
      'Fitness Machine Status',
      'Five Zone Heart Rate Limits',
      'Floor Number',
      'Central Address Resolution',
      'Device Name',
      'Peripheral Preferred Connection Parameters',
      'Peripheral Privacy Flag',
      'Reconnection Address',
      'Service Changed',
      'Gender',
      'Glucose Feature',
      'Glucose Measurement',
      'Glucose Measurement Context',
      'Gust Factor',
      'Hardware Revision String',
      'Heart Rate Control Point',
      'Heart Rate Max',
      'Heart Rate Measurement',
      'Heat Index',
      'Height',
      'HID Control Point',
      'HID Information',
      'Hip Circumference',
      'HTTP Control Point',
      'HTTP Entity Body',
      'HTTP Headers',
      'HTTP Status Code',
      'HTTPS Security',
      'Humidity',
      'IDD Annunciation Status',
      'IDD Command Control Point',
      'IDD Command Data',
      'IDD Features',
      'IDD History Data',
      'IDD Record Access Control Point',
      'IDD Status',
      'IDD Status Changed',
      'IDD Status Reader Control Point',
      'IEEE 11073-20601 Regulatory Certification Data List',
      'Indoor Bike Data',
      'Indoor Positioning Configuration',
      'Intermediate Cuff Pressure',
      'Intermediate Temperature',
      'Irradiance',
      'Language',
      'Last Name',
      'Latitude',
      'LN Control Point',
      'LN Feature',
      'Local East Coordinate',
      'Local North Coordinate',
      'Local Time Information',
      'Location and Speed Characteristic',
      'Location Name',
      'Longitude',
      'Magnetic Declination',
      'Magnetic Flux Density – 2D',
      'Magnetic Flux Density – 3D',
      'Manufacturer Name String',
      'Maximum Recommended Heart Rate',
      'Measurement Interval',
      'Mesh Provisioning Data In',
      'Mesh Provisioning Data Out',
      'Mesh Proxy Data In',
      'Mesh Proxy Data Out',
      'Model Number String',
      'Navigation',
      'Network Availability',
      'New Alert',
      'Object Action Control Point',
      'Object Changed',
      'Object First-Created',
      'Object ID',
      'Object Last-Modified',
      'Object List Control Point',
      'Object List Filter',
      'Object Name',
      'Object Properties',
      'Object Size',
      'Object Type',
      'OTS Feature',
      'PLX Continuous Measurement Characteristic',
      'PLX Features',
      'PLX Spot-Check Measurement',
      'PnP ID',
      'Pollen Concentration',
      'Position 2D',
      'Position 3D',
      'Position Quality',
      'Pressure',
      'Protocol Mode',
      'Pulse Oximetry Control Point',
      'Rainfall',
      'RC Feature',
      'RC Settings',
      'Reconnection Configuration Control Point',
      'Record Access Control Point',
      'Reference Time Information',
      'Registered User Characteristic',
      'Removable',
      'Report',
      'Report Map',
      'Resolvable Private Address Only',
      'Resting Heart Rate',
      'Ringer Control point',
      'Ringer Setting',
      'Rower Data',
      'RSC Feature',
      'RSC Measurement',
      'SC Control Point',
      'Scan Interval Window',
      'Scan Refresh',
      'Scientific Temperature Celsius',
      'Secondary Time Zone',
      'Sensor Location',
      'Serial Number String',
      'Server Supported Features',
      'Service Required',
      'Software Revision String',
      'Sport Type for Aerobic and Anaerobic Thresholds',
      'Stair Climber Data',
      'Step Climber Data',
      'String',
      'Supported Heart Rate Range',
      'Supported Inclination Range',
      'Supported New Alert Category',
      'Supported Power Range',
      'Supported Resistance Level Range',
      'Supported Speed Range',
      'Supported Unread Alert Category',
      'System ID',
      'TDS Control Point',
      'Temperature',
      'Temperature Celsius',
      'Temperature Fahrenheit',
      'Temperature Measurement',
      'Temperature Type',
      'Three Zone Heart Rate Limits',
      'Time Accuracy',
      'Time Broadcast',
      'Time Source',
      'Time Update Control Point',
      'Time Update State',
      'Time with DST',
      'Time Zone',
      'Training Status',
      'Treadmill Data',
      'True Wind Direction',
      'True Wind Speed',
      'Two Zone Heart Rate Limit',
      'Tx Power Level',
      'Uncertainty',
      'Unread Alert Status',
      'URI',
      'User Control Point',
      'User Index',
      'UV Index',
      'VO2 Max',
      'Waist Circumference',
      'Weight',
      'Weight Measurement',
      'Weight Scale Feature',
      'Wind Chill']

CK_codes = [ck.replace('0x', '') for ck in CK]
ble_char_dict = dict(zip(CK_codes, TK))
ble_char_dict_rev = dict(zip(TK, CK_codes))


# XML PARSER --> get char tag and return char_xml class

class CHAR_XML:
    def __init__(self, xml_file):
        self._tree = ET.parse("{}/{}".format(CHARS_XML_DIR, xml_file))
        with open("{}/{}".format(CHARS_XML_DIR, xml_file), 'rb') as xmlfileraw:
            self._raw = xmlfileraw.read().decode()
        self._root = self._tree.getroot()
        self.char_metadata = None
        self.name = None
        self.char_type = None
        self.uuid = None
        self.field_name = None
        self.info_text = None
        self.note = ''
        self.requirment = None
        self.data_format = None
        self.fmt = None
        self.unit_stringcode = None
        self.unit = None
        self.unit_symbol = None
        self.quantity = None
        self.unit = None
        self.abstract = None
        self.summary = None
        self.description = None
        self.minimum = None
        self.maximum = None
        self.dec_exp = None
        self.xml_tags = {}
        self.fields = {}
        self.actual_field = None
        self.bitfields = {}
        self.actual_bitfield = None
        self.actual_bit = None
        self.get_data()
        self.get_fields()

    def get_data(self):
        for val in self._root.iter():
            try:
                if hasattr(val.text, 'strip'):
                    self.xml_tags[val.tag] = [val.text.strip(), val.attrib]
                else:
                    self.xml_tags[val.tag] = [val.text, val.attrib]
                if val.tag == 'Characteristic':
                    self.char_metadata = val.attrib
                    self.name = self.char_metadata['name']
                    self.char_type = self.char_metadata['type']
                    self.uuid = self.char_metadata['uuid']
                if val.tag == 'Field':
                    self.field_name = val.attrib['name']
                if val.tag == 'BitField':
                    self.bitfields[val.tag] = {}
                    self.actual_bitfield = val.tag
                if val.tag == 'Bit':
                    if self.bitfields.keys():
                        if 'name' in val.attrib.keys():
                            bitname = val.attrib['name']
                        else:
                            bitname = "Bit {}".format(val.attrib['index'])
                        self.bitfields[self.actual_bitfield][bitname] = {}
                        self.bitfields[self.actual_bitfield][bitname]['index'] = val.attrib['index']
                        self.bitfields[self.actual_bitfield][bitname]['size'] = val.attrib['size']
                        self.actual_bit = bitname
                if val.tag == 'Enumeration':
                    if self.actual_bitfield is not None:
                        if self.bitfields[self.actual_bitfield].keys():
                            self.bitfields[self.actual_bitfield][self.actual_bit]['Enumerations'][val.attrib['key']] = val.attrib['value']
                if val.tag == 'Enumerations':
                    if self.actual_bitfield is not None:
                        if self.bitfields[self.actual_bitfield].keys():
                            self.bitfields[self.actual_bitfield][self.actual_bit][val.tag] = {}
                if val.tag == 'Abstract':
                    if hasattr(val.text, 'strip'):
                        self.abstract = val.text.strip()
                    else:
                        self.abstract = val.text
                if val.tag == 'Summary':
                    if hasattr(val.text, 'strip'):
                        self.summary = val.text.strip()
                    else:
                        self.summary = val.text
                if val.tag == 'Description':
                    if hasattr(val.text, 'strip'):
                        self.description = val.text.strip()
                    else:
                        self.description = val.text
                if val.tag == 'Maximum':
                    if hasattr(val.text, 'strip'):
                        self.maximum = val.text.strip()
                    else:
                        self.maximum = val.text
                if val.tag == 'Minimum':
                    if hasattr(val.text, 'strip'):
                        self.minimum = val.text.strip()
                    else:
                        self.minimum = val.text
                if val.tag == 'InformativeText':
                    if hasattr(val.text, 'strip'):
                        self.info_text = val.text.strip()
                    else:
                        self.info_text = val.text
                if val.tag == 'Note':
                    if hasattr(val.text, 'strip'):
                        self.note = val.text.strip()
                    else:
                        self.note = val.text
                if val.tag == 'p':
                    if hasattr(val.text, 'strip'):
                        if self.note is None:
                            self.note = ''
                        self.note += val.text.strip() + '\n'
                if val.tag == 'Requirement':
                    self.requirment = val.text
                if val.tag == 'Format':
                    self.data_format = val.text
                    self.fmt = DATA_FMT[self.data_format]
                if val.tag == 'Unit':
                    self.unit_stringcode = val.text
                    # get unit from unit stringcode
                    unit_stringcode_filt = self.unit_stringcode.replace(
                        "org.bluetooth.unit.", '')
                    self.quantity = ' '.join(
                        unit_stringcode_filt.split('.')[0].split('_'))
                    try:
                        self.unit = ' '.join(
                            unit_stringcode_filt.split('.')[1].split('_'))
                        self.unit_symbol = ble_SI_units_dict[self.unit]
                    except Exception as e:
                        try:
                            self.unit = self.quantity
                            self.unit_symbol = ble_SI_units_dict[self.unit]
                        except Exception as e:
                            self.unit = ''
                            self.unit_symbol = ''
                    # get unit_symbol
                if val.tag == 'DecimalExponent':
                    self.dec_exp = int(val.text)
            except Exception as e:
                print(traceback.format_exc())

    def get_fields(self):
        for val in self._root.iter():
            try:
                if val.tag == 'Field':
                    self.fields[val.attrib['name']] = {}
                    self.actual_field = val.attrib['name']

                if val.tag == 'Maximum':
                    if hasattr(val.text, 'strip'):
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text.strip()
                    else:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] =  val.text
                if val.tag == 'Minimum':
                    if hasattr(val.text, 'strip'):
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text.strip()
                    else:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text
                if val.tag == 'Requirement':
                    try:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text
                    except Exception as e:
                        print(e)
                if val.tag == 'Format':
                    # self.data_format = val.text
                    # self.fmt = DATA_FMT[self.data_format]
                    if self.fields.keys():
                        self.fields[self.actual_field][val.tag] = val.text
                        self.fields[self.actual_field]['Ctype'] = DATA_FMT[val.text]
                if val.tag == 'Enumeration':
                    if self.fields.keys():
                        if 'Enumerations' in self.fields[self.actual_field].keys():
                            self.fields[self.actual_field]['Enumerations'][val.attrib['key']] = val.attrib['value']
                        else:
                            self.fields[self.actual_field]['Enumerations'] = {}
                            self.fields[self.actual_field]['Enumerations'][val.attrib['key']] = val.attrib['value']

                if val.tag == 'Enumerations':
                    if self.fields.keys():
                        self.fields[self.actual_field][val.tag] = {}
            except Exception as e:
                print(traceback.format_exc())


def get_XML_CHAR(char):
    if "Magnetic Flux" in char:
        char_string = "_".join([ch.lower().replace('magnetic', 'Magnetic')
                                for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
        char_string = char_string.replace('3d', '3D').replace('2d', '2D')
    else:
        char_string = "_".join([ch.lower()
                                for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
    char_string += '.xml'
    char_string = char_string.replace('_characteristic', '')
    return CHAR_XML(char_string)


def get_raw_XML_CHAR(char):
    if "Magnetic Flux" in char:
        char_string = "_".join([ch.lower().replace('magnetic', 'Magnetic')
                                for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
        char_string = char_string.replace('3d', '3D').replace('2d', '2D')
    else:
        char_string = "_".join([ch.lower()
                                for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
    char_string = char_string.replace('_characteristic', '')
    with open("{}/{}.xml".format(CHARS_XML_DIR, char_string), 'rb') as xmlfileraw:
        return xmlfileraw.read().decode()
