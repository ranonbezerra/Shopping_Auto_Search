# Shopping_Auto_Search
 An RPA to search for products in a list from a spreadsheet.
 
 - This automation gets products names, price range, forbidden websites and words from a xlsx file to export another file with the same extention with the results title, price and link;
 - The version here search exclusively on Google Shopping;
 - The automation check if the product title found on the search has all the words in the products name;
 - For example, if you do a regular search on google shopping for an iPhone 14 Pro, you will sometimes get as resulting match an iPhone 13 Pro, or an regular iPhone 14. This automation make sure that these results does not show up on the exported xlsx file;
 - The user is able to update the database, which comes from the xlsx file named 'products.xlsx' and change the corresponding columns to more fitting ones
 - Any suggestion are welcome!   
