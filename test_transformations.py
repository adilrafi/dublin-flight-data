# Transform a raw callsign into a 3 letter ariline code

def extract_airline_code(callsign):
  if not callsign or len(str(callsign).strip()) < 3:
    return "N/A"

  return str(callsign).strip()[:3]


# Unit test code for extract_airline_code function

import unittest

class TestFlightData(unittest.TestCase):

  def test_extract_airline_code(self):

    # Test for Aer Lingus
    self.assertEqual(extract_airline_code("EIN7JC  "), "EIN")

    # Test for Ryanair
    self.assertEqual(extract_airline_code("RYR6CM  "), "RYR")

    # Test for United Airlines
    self.assertEqual(extract_airline_code("UAL980  "), "UAL")

    # Test for Delta Airline
    self.assertEqual(extract_airline_code("DAL176  "), "DAL")

    # Test Empty or short callsign (less than 3)
    self.assertEqual(extract_airline_code(""), "N/A")
    self.assertEqual(extract_airline_code(None), "N/A")

if __name__ == '__main__':

  unittest.main(argv=[''], exit=False)
