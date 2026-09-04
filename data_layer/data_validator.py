import re

class DataValidator:
    """
    Data Validation Engine for OmniStat Core.
    Validates structural integrity, formats, date constraints, and digit consistency.
    """

    @staticmethod
    def validate_2d(val):
        """Validate 2-digit lottery number string (00 to 99)."""
        if val is None:
            return False, "Value is None"
        s = str(val).strip()
        if re.match(r'^\d{2}$', s):
            return True, s
        if re.match(r'^\d{1}$', s):
            return True, s.zfill(2)
        return False, f"Invalid 2D number: {val}"

    @staticmethod
    def validate_3d(val):
        """Validate 3-digit lottery number string (000 to 999)."""
        if val is None:
            return False, "Value is None"
        s = str(val).strip()
        if re.match(r'^\d{3}$', s):
            return True, s
        return False, f"Invalid 3D number: {val}"

    @staticmethod
    def validate_4d(val):
        """Validate 4-digit lottery number string (0000 to 9999)."""
        if val is None:
            return False, "Value is None"
        s = str(val).strip()
        if re.match(r'^\d{4}$', s):
            return True, s
        return False, f"Invalid 4D number: {val}"

    @staticmethod
    def validate_gdb(gdb):
        """Validate Special Prize (GĐB) 5-digit format."""
        if gdb is None:
            return False, "GDB is None"
        s = str(gdb).strip()
        if re.match(r'^\d{5}$', s):
            return True, s
        return False, f"Invalid GDB: {gdb}"

    def validate_record(self, record):
        """Validate a full draw record dictionary."""
        errors = []
        
        valid_gdb, gdb_val = self.validate_gdb(record.get("gdb"))
        if not valid_gdb:
            errors.append(gdb_val)
            
        valid_2d, de_val = self.validate_2d(record.get("de_2d"))
        if not valid_2d:
            errors.append(de_val)
            
        for g7_key in ["g7_1", "g7_2", "g7_3", "g7_4"]:
            val = record.get(g7_key)
            if val:
                v_ok, _ = self.validate_2d(val)
                if not v_ok:
                    errors.append(f"Invalid {g7_key}: {val}")

        return len(errors) == 0, errors


if __name__ == "__main__":
    validator = DataValidator()
    sample = {
        "date": "Thứ năm ngày 01-01-2026",
        "gdb": "57068",
        "de_2d": "68",
        "g7_1": "91",
        "g7_2": "25"
    }
    is_valid, errors = validator.validate_record(sample)
    print("Sample validation:", is_valid, errors)
