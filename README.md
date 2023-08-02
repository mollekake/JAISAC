# JAISAC

(Justwatch And Imdb Scraper And Comparator)

A very basic and hacky way to get your personal IMDb watchlist, get all the titles, and check on JustWatch where you can stream said titles.

Currently it only works with up to 200 titles.
It only works with personal watchlists, and not publicly made watchlists.

It uses tkinter to create a GUI. 
This is not command-line based app.

How it works:
1 - Type in the country code where you are, or the country you wish to get streaming services from.

  (This is because JustWatch shows streaming services that is in your country)
  
2 - Type in your IMDb username, it usualy starts with "ur"

  (It is found between "https://www.imdb.com/user/" and "/watchlist"
  
3 - Click the button

The app then does the following:

1 - Gets your personal IMDb watchlist and makes a list of all the titles

2 - Goes through every title

3 - Checks on JustWatch based on title name on which streaming services based in your country that you can watch the title on

4 - Creates 3 lists of your titles.

  a - The movies and shows it found you can watch on streaming services, and which services to watch them on
  
  b - The movies and shows it did not find on any streaming services
  
  c - The movies and shows it did not find on JustWatch at all.
  
    (That usually comes from weird titles, duplicate titles, foreign titles etc.)

This is what the app looks like:

![Skjermbilde 2023-08-02 165347](https://github.com/mollekake/JAISAC/assets/2526461/35565fba-703f-4dcd-8742-7951c7dec9a6)
