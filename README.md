# Image Scraping

画像ファイルを検索して収集する。

検索キーワードを示す場合：


```
$ python imagescraping.py -t "japanese kimono" -d save_directory
```

類似画像を検索する場合。画像を右クリックして、「Googleで画像を選択」を選ぶと、google画像検索のページに飛ぶ。そこで「類似画像を検索」で飛ぶページのURLを記録する。そのようにして集めたURLのリストを、search_url_list.txt に保存する。このURLリストから画像を取得していく。

```
$ python imagescraping.py -u search_url_list.txt -d save_directory
```

Note: multithreadの終了を確認していないのでコマンドが途中で止まってしまうようにみえる。出力がなくなれば終了。



