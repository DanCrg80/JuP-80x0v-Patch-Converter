# Roland JP-80x0 Checksum Calculator by DanCrg (2025)
# A utility for calculating and extracting checksums from Roland JP-80x0 SysEx data

class RolandJP80x0ChecksumCalc:
    def __init__(self):
        self.sysex_data = []
        self.patch_data = []
        
    def parse_sysex_message(self, hex_string):
        # Parse a SysEx message from hex string format

        # Remove spaces and convert to list of integers
        hex_bytes = hex_string.replace(' ', '')
        self.sysex_data = [int(hex_bytes[i:i+2], 16) for i in range(0, len(hex_bytes), 2)]
        
        # Validate SysEx structure
        if len(self.sysex_data) < 8:
            raise ValueError("SysEx message too short")
        
        if self.sysex_data[0] != 0xF0:
            raise ValueError("Invalid SysEx start byte")
            
        if self.sysex_data[-1] != 0xF7:
            raise ValueError("Invalid SysEx end byte")
        
        # Extract Roland header information
        self.manufacturer_id = self.sysex_data[1]  # Should be 0x41 for Roland
        self.device_id = self.sysex_data[2]        # Device ID
        self.model_id1 = self.sysex_data[3]        # Should be 0x00
        self.model_id2 = self.sysex_data[4]        # Should be 0x06 for JP-80x0
        self.command = self.sysex_data[5]          # Should be 0x12 for Data Set
        
        # Extract address (4 bytes)
        self.address = self.sysex_data[6:10]
        
        # Extract patch data (everything between address and checksum+F7)
        self.patch_data = self.sysex_data[10:-2]
        
        # Extract checksum
        self.transmitted_checksum = self.sysex_data[-2]
        
        return self.patch_data
    
    def calculate_roland_checksum(self, data=None):

        # Calculate Roland checksum using the standard Roland algorithm:
        # 1. Sum all data bytes (address + data)
        # 2. Take the lower 7 bits of the sum
        # 3. Subtract from 128
        # 4. Take the lower 7 bits of the result

        if data is None:
            # Use address + patch data for checksum calculation
            data_to_check = self.address + self.patch_data
        else:
            data_to_check = data
            
        # Sum all bytes
        total_sum = sum(data_to_check)
        
        # Roland checksum algorithm
        checksum = (128 - (total_sum % 128)) % 128
        
        return checksum
    
    def extract_checksum(self):
        # Extract the checksum from the parsed SysEx message

        if not self.sysex_data:
            raise ValueError("No SysEx data loaded. Call parse_sysex_message first.")
        
        return self.transmitted_checksum
    
    def verify_checksum(self):
        # Verify that the transmitted checksum matches the calculated checksum

        calculated = self.calculate_roland_checksum()
        transmitted = self.extract_checksum()
        
        return calculated == transmitted
    
    def get_patch_name(self):
        # Extract the patch name from the patch data (first 16 bytes are usually the name)

        if len(self.patch_data) >= 16:
            try:
                # Try to decode as ASCII, replacing non-printable characters
                name_bytes = self.patch_data[:16]
                name = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in name_bytes)
                return name.rstrip('\x00 ')  # Remove null terminators and trailing spaces
            except:
                return "Unable to decode name"
        return "No name data"
    
    def analyze_sysex_structure(self):
        # Analyze and display the structure of the SysEx message

        if not self.sysex_data:
            raise ValueError("No SysEx data loaded. Call parse_sysex_message first.")
        
        analysis = {
            'total_length': len(self.sysex_data),
            'manufacturer': f"0x{self.manufacturer_id:02X} ({'Roland' if self.manufacturer_id == 0x41 else 'Unknown'})",
            'device_id': f"0x{self.device_id:02X}",
            'model_id': f"0x{self.model_id1:02X} 0x{self.model_id2:02X} ({'JP-80x0' if self.model_id2 == 0x06 else 'Unknown'})",
            'command': f"0x{self.command:02X} ({'Data Set' if self.command == 0x12 else 'Unknown'})",
            'address': ' '.join(f"0x{b:02X}" for b in self.address),
            'data_length': len(self.patch_data),
            'transmitted_checksum': f"0x{self.transmitted_checksum:02X}",
            'calculated_checksum': f"0x{self.calculate_roland_checksum():02X}",
            'checksum_valid': self.verify_checksum(),
            'patch_name': self.get_patch_name()
        }
        
        return analysis
    
    def display_analysis(self):
        # Display a formatted analysis of the SysEx message
        
        analysis = self.analyze_sysex_structure()
        
        print("Roland JP-80x0 SysEx Analysis")
        print("=" * 50)
        print(f"Total Length:         {analysis['total_length']} bytes")
        print(f"Manufacturer:         {analysis['manufacturer']}")
        print(f"Device ID:            {analysis['device_id']}")
        print(f"Model ID:             {analysis['model_id']}")
        print(f"Command:              {analysis['command']}")
        print(f"Address:              {analysis['address']}")
        print(f"Data Length:          {analysis['data_length']} bytes")
        print(f"Transmitted Checksum: {analysis['transmitted_checksum']}")
        print(f"Calculated Checksum:  {analysis['calculated_checksum']}")
        print(f"Checksum Valid:       {analysis['checksum_valid']}")
        
    def create_sysex_message(self, patch_data, device_id=0x10, address=[0x02, 0x00, 0x00, 0x00]):
        # Create a complete SysEx message with proper checksum

        # Start with SysEx header
        message = [0xF0, 0x41, device_id, 0x00, 0x06, 0x12]
        
        # Add address
        message.extend(address)
        
        # Add patch data
        message.extend(patch_data)
        
        # Calculate and add checksum
        checksum = self.calculate_roland_checksum(address + patch_data)
        message.append(checksum)
        
        # Add SysEx end
        message.append(0xF7)
        
        return message
    
    def format_as_hex_string(self, data):
        # Format byte data as hex string
        return ' '.join(f"{b:02X}" for b in data)


def main():
    # Example usage with the provided JP-80x0 patch data
    
    # The provided SysEx message
    sysex_hex = ("F0 41 10 00 06 12 03 00 08 00 00 00 00 00 00 01 01 00 0A 60 04 00 3C 3C 50 64 7F 7F 7F 7F 7F 7F 78 6E 20 40 00 40 7F 60 00 0A 32 40 00 00 40 40 00 00 00 7E F7")
    
    calc = RolandJP80x0ChecksumCalc()
    
    print("Roland JP-80x0 Checksum Calculator")
    print("=" * 50)
    
    # Parse the SysEx message
    patch_data = calc.parse_sysex_message(sysex_hex)
    
    # Display analysis
    calc.display_analysis()
    
    print(f"\nExtracted checksum:   0x{calc.extract_checksum():02X}")
    print(f"Data length:          {len(patch_data)} bytes")
    
    # Test creating a new message with the same data
    print(f"\nTesting message recreation...")
    new_message = calc.create_sysex_message(patch_data, device_id=calc.device_id, address=calc.address)
    new_hex = calc.format_as_hex_string(new_message)
    
    print(f"Original matches recreated: {sysex_hex.replace(' ', '') == new_hex.replace(' ', '')}")


if __name__ == "__main__":
    main()
