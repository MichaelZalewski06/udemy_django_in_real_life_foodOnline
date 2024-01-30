import datetime

def generate_order_number( pk ):
  current_datetime = datetime.datetime.now().strftime( '%Y%m%d' )
  return current_datetime + str( pk )