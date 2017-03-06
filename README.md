# calendar_parser
File that scrapes sites for information about booking flats for a day.

Now function works with 7 sites(examples below), but you can add your own.

Links to try the function(some random apartments):  
http://www.dobovo.com/kiev-apartments/vey-spacious-apartment-near-independence-square-92177.html  
https://oktv.ua/id3093608  
http://www.partnerguesthouse.com/en/Basseynaya-19-KV179  
https://www.airbnb.com/rooms/16435808  
https://www.tripadvisor.com/VacationRentalReview-g60763-d4126179-Brand_New_Spacious_Times_square_3BR_on_39st-New_York_City_New_York.html  
https://www.9flats.com/places/150320-apartment-new_york_city-manhattanville  
http://www.wimdu.com/offers/3ML6M0PJ  

Example of using: 

$python calendar_parser.py https://www.airbnb.com/rooms/16435810

('2017-03-01', 'Unavailable'),  
 ('2017-03-02', 'Unavailable'),  
 ('2017-03-03', 'Unavailable'),  
 ('2017-03-04', 'Unavailable'),  
 ('2017-03-05', 'Unavailable'),  
 ('2017-03-06', 'Unavailable'),  
 ('2017-03-07', 'Available'),  
 ('2017-03-08', 'Available'),  
 ('2017-03-09', 'Unavailable'),  
 and so on...
