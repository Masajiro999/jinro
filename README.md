# jinro  
元々http://park1.wakwak.com/~aa1/table/jinro.zipにあったソースをアップロードしています。  
問題があれば即刻削除します。  
  
ソース作成者のaduma氏より許可を得たわけではありません。  
当時公開されていたソースコードを代理のつもりで公開しています。  
人狼のCGIの勉強等にお使いください。  
  
以下設置方法内容をそのまま転機しておきます  
--  
○ファイル構成  
[public_html]  
┣　jinro_index.htm  
┃　jinro_rule.htm  
┃　[img]  
┃  
┗[cgi-bin]  
　┣　cgi_jinro.cgi [755]  
　┃　[lock] [777]  
  
○アップ手順  
１．ファイルの修正をします。  
　・jinro_index.htm  
　登録、ログイン、管理者のリンク先をＣＧＩを設置するパスに直して下さい。  
　・cgi_jinro.cgi  
　１行目をプロバイダに仕様にあわせてください。  
　設定開始～設定終了までの項目を設置場所にあわせて修正してください。  
　この時パスワードはランダムなものに修正してください。  
  
２．ファイルのアップロード  
　・上記のファイル構成を参考にホームのディレクトリにhtmファイルを置きます。  
　「img」という名前のフォルダを作成してその中に画像ファイルを設置します。  
　・ＣＧＩフォルダに移動してcgiファイルを設置します。  
　属性を[755]に変更します。  
　「lock」という名前のフォルダを作成し、属性を[777]にします。  
  
３．動作確認  
　設置したjinro_index.htmにアクセスして「管理者ログイン」をします。  
　「村を作成」を選択してパスワードを入力し実行します。  
　村が作成されて村に登録できるかをチェックしてください。  
　ここまで正しく動いたら管理者でログインして一度「強制終了」させて  
　「村の削除」を行ってください。  
  
４．運営  
　「村の作成」により村を増やせます。  
　作成した村には管理者としてログインが可能です。  
　管理者としてログインした場合、特殊なコマンドがあります。  
　「ゲームの開始」は最も重要な役目でその村のゲームを開始します。  
　プレイヤーが８名以上の場合のみ実行可能です。  
　メッセージ系は時間を気にせず書きこみができます。  
　「突然死」は強制的にプレイヤーを死亡させます。  
　都合上参加できなくなってしまったプレイヤーに適用してください。  
　この時このコマンドで勝敗が決まってしまうような場合、  
　スクリプトでは対処していません。  
　運営不可能と判断した場合はプレイヤーの許可をとってゲームの強制終了を  
　したほうが良いと思います。  
　「投票の再集計」は「突然死」を適用した場合に投票が終了できない状態になるのを  
　防ぐために再度集計する処理ですので通常は使用しません。  
  
　以上基本的に管理者は「ゲームの開始」を行った後は割りと見るだけです。  
　村にはあまりメッセージを出さない方が良いと思いますが  
　そこは各管理者の独自の判断で運営してください。  
  
　最後ですがスクリプトの改変は自由です。  
　アイコンも全て私の自作なんで自由にいじってください。  
　ぜひ、良い村を運営しください。  
  
　以上。  
