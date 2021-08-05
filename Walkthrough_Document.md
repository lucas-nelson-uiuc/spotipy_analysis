# WALKTHROUGH DOCUMENT
Please review this document to properly gather, view, and interact with the data necessary for `Spotify Analysis Dashboard`

### Table of Contents

* [Generating Your Spotify Token](#Generating-Your-Spotify-Token)
* [Gathering Your Spotify Playlist URLs](#Gathering-Your-Spotify-Playlist-URLs)
* [Reviewing Your Input Data](#Reviewing-Your-Input-Data)
* [Your Unique Spotify Analysis Dashboard](#Your-Unique-Spotify-Analysis-Dashboard)
* [Interacting with Plotly Graphs](#Interacting-with-Plotly-Graphs)

---
# Generating Your Spotify Token
This section will walk you through how to generate a Spotify token by accessing your `CLIENT ID` and `CLIENT SECRET`. To learn more about what a "token" is and why Spotify requires it, visit the [What is a Spotify Token](#What-is-a-Spotify-Token) section at the bottom of this page.

### 01. Spotify Developer Dashboard
* Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/). If you have a Spotify account, select `LOG IN`. If you do not have a Spotify account, select `CREATE AN ACCOUNT`.

![Descriptive Image #01](https://i.imgur.com/xuHd84L.png)

* Once you have entered your Spotify Developer Dashboard, create an app by either selecting `CREATE AN APP` or clicking on any of the app boxes below.

![Descriptive Image #02](https://i.imgur.com/xWFR5Rf.png)

* Enter any random `name` and `description` for your app. (These will not be used in further steps.) Afterwards, review and agree to the `Terms of Service` then select `CREATE`.

![Descriptive Image #03](https://i.imgur.com/IA7bPoQ.png)

* Copy your `CLIENT ID` and `CLIENT SECRET`.

![Descriptive Image #04](https://i.imgur.com/YMyLGKy.png)

* Finally, paste both into respective fields in `Spotify Analysis Dashboard`, located in the `Enter Input Data` tab in the sidebar.

![Descriptive Image #05](https://i.imgur.com/FgXRXEs.png)

---
# Gathering Your Spotify Playlist URLs
This section will walk you through how to gather your Spotify playlist URL(s).

### 01. Login to Spotify
Visit [Spotify](https://open.spotify.com/). If you have a Spotify account, select `LOG IN`. If you do not have a Spotify account, select `CREATE AN ACCOUNT`.

### 02. Gather Playlist URLs
Once you have entered Spotify, gather your playlist URLs one-by-one. Since `Spotify Analysis Dashboard` uses your token to gather the data, you only have access to playlists created under your account and public playlists created by any account.

Your URL should look like this: `https://open.spotify.com/playlist/37i9dQZF1DXe8E8oqpmTDI`

### 03. Paste Playlist URL
Once you have a playlist's URL, individually paste it into the `Playlist URL(s)` text field under `Enter Input Data`. Ensure that playlist follows the format from the section above.

If you have multiple playlists, there must be a comma separating the end of one playlist URL and the beginning of another playlist URL. Whitespace may be used as well, but a comma is necessary.

After inserting your playlist URL(s), the text field should look like this:

![Descriptive Image 05](https://i.imgur.com/KR49qJj.png)

### 04. Ready to Go
After pasting your `CLIENT ID`, `CLIENT SECRET`, and `Playlist URL(s)`, your `Enter Input Data` section should look something similar to this. Note, playlist URLs do not have to be aligned nor have consistent whitespace, **they only need commas separating the URLs**.
```
Enter Input Data
¦   Client ID
+---   A0****************************z9
¦   Client Secret
+---   b1****************************Y8
¦   Playlist URL(s)
+---   https://open.spotify.com/playlist/37i9dQZF1DXe8E8oqpmTDI  ,
       https://open.spotify.com/playlist/37i9dQZF1DZ06evO0ti1Ik,
         https://open.spotify.com/playlist/37i9dQZF1E4rdgTEVYvWfZ   ,
       https://open.spotify.com/playlist/37i9dQZF1DZ06evO3zDJMk ,
        https://open.spotify.com/playlist/37i9dQZF1DX2zsdpDHp0xI
``` 
---

If you'd like to see your dashboard as soon as possible, you may skip the rest of the document and select `Gather DataFrame` in the `Enter Input Data` section and then further explore in the `Select Data` section.

If you'd like to read more about certain individual components of the dashboard, please continue reading, although not necessary.

---
# Reviewing Your Input Data
After gathering your input data, select `Gather DataFrame` to begin the data gathering process. Depending on the size of your playlist(s), this may take a few minutes (~380 songs per minute). This will take you to the `Data Review Screen`. At the moment, this screen will simply be the page for you to understand your data prior to analyzing your data. However, there are plans to include user input functionality that would allow the user to modify missing and mislabeled data.

---
# Your Unique Spotify Analysis Dashboard
The `Spotify Analysis Dashboard` comes with the following six dashboards: `Brief History`, `Track`, `Artists + Albums`, `Listening Trends`, `Random Statistics`, and `Recommendations [Beta]`. Each page has its own unique purpose, but they all sample from the same dataset provided in the `Enter Input Data` section.

Most graphs follow the same format: title, description, data filtering, graph. Titles briefly mention the purpose of its section of the page. Descriptions are hidden in expanding boxes (click to open/close) and fully explain how to interact with the graph. Data filtering tools are in place to allow the user to further refine the default state of the final element, the graph. (See below for graph interaction.)

---
# Interacting with Plotly Graphs
The graphs utilized by your dashboard were made possible by [Plotly](https://plotly.com/python/), an open source graphing library for multiple programming languages. These graphs were selected for an array of reasons, but since chances are you'll be seeing your music listening data for the first time, it'd be best if you could interact with it, right?

Interaction with Plotly graphs go beyond visualizing data: it also means filtering, manipulating, searching, etc. This section of the document will briefly cover some of these Plotly functionalities to enhance your experience exploring your data.

### Plotly Graph Toolbar
Each Plotly graph is equipped with the following toolbar, located in the upper right corner and activated by hovering over the graph. The purpose of these tools are to either magnify your view of the graph (zooming, full-screen), filter the data used for the graph (box-select, lasso-select), or compare data across the graph (show data on hover).

![Plotly Toolbar](https://i.imgur.com/tCqRECo.png)

Although each graph's trends can be noted easily, I recommend utilizing the full-screen option when possible to analyze individual data points more clearly.

### Plotly Graph Legends
Plotly graphs may also be equipped with a legend as a way of further filtering data. Although its purpose is to label data, single-clicking an item will remove it from the graph and double-clicking an item will make it the only item in the graph. Filtering can be reversed by performing the action again.

![Plotly Legend](https://i.imgur.com/N8Z6Jo3.png)
