#!/usr/local/bin/perl

#===========================================================
# jinro: Version 2004.02.02a
#===========================================================

require './jcode.pl';

#-[ 設定開始 ]-----------------------------------------------------------

# ゲーム名
$sys_title = "「汝は人狼なりや？」スクリプト";
# 画像フォルダ
$imgpath = "http://www.xxx.co.jp/~yyy/img/";
#CGI パスファイル名
$cgi_path = "http://www.xxx.co.jp/~yyy/cgi-bin/cgi_jinro.cgi";
# プレイヤーデータ パスファイル名 (拡張子無し)
$dat_path = "./dat_jinro";
# ログデータ パスファイル名 (拡張子無し)
$log_path = "./dat_jinrolog";
# 戻りパス
$return_url = "http://www.xxx.co.jp/~yyy/jinro_index.htm";
# ロックファイル パス
$lock_path = "./lock/jinro.loc";
# PASSWORD
$sys_pass = 'pass';

#キャラクター
$chr_hum = '村　人';
$chr_wlf = '人　狼';
$chr_ura = '占い師';
$chr_nec = '霊能\者';
$chr_mad = '狂　人';
$chr_fre = '共有者';
$chr_bgd = '狩　人';
$chr_fox = '妖　狐';

#-[ 設定終了 ]-----------------------------------------------------------

$ENV{'TZ'} = "JST-9";

$wk_color[1] = "#DDDDDD";
$wk_color[2] = "#999999";
$wk_color[3] = "#FFFF33";
$wk_color[4] = "#FF9900";
$wk_color[5] = "#FF0000";
$wk_color[6] = "#99CCFF";
$wk_color[7] = "#0066FF";
$wk_color[8] = "#00EE00";
$wk_color[9] = "#CC00CC";
$wk_color[10] = "#FF9999";


# Japanese KANJI code
if (-f "jcode.pl") {
	$jflag = 1;
	require "jcode.pl";
	$code = ord(substr("漢", 0, 1));
	if ($code == 0xb4) {
		$ccode = "euc";
	} elsif ($code == 0x1b) {
		$ccode = "jis";
	} else {
		$ccode = "sjis";
	}
}

# Read variables
if ($ENV{'REQUEST_METHOD'} eq "POST") {
	read(STDIN, $query_string, $ENV{'CONTENT_LENGTH'});
	@a = split(/&/, $query_string);
	foreach $x (@a) {
		($name, $value) = split(/=/, $x);
		$value =~ tr/+/ /;
		$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;
		if ($jflag) {
			&jcode'convert(*value, "euc");
		}
		$value =~ s/&/&amp;/g;
		$value =~ s/"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
		if ($jflag) {
			&jcode'convert(*value, $ccode);
		}
		$FORM{$name} = $value;
		
	}
}


# File lock
foreach $i ( 1, 2, 3, 4, 5, 6 ) {
        if (mkdir($lock_path, 0755)) {
                last;
        } elsif ($i == 1) {
                ($mtime) = (stat($lock_path))[9];
                if ($mtime < time() - 600) {
                        rmdir($lock_path);
                }
        } elsif ($i < 6) {
                sleep(2);
        } else {
                &disp_head1;
                print "<H1>ファイルロック</H1>\n";
                print "再度アクセスお願いします。<BR>\n";
                print "<A href='javascript:window.history.back()'>戻る</A>\n";
                &disp_foot;
                exit(1);
        }
}

# Remove lockfile when terminated by signal
sub sigexit { rmdir($lock_path); exit(0); }
$SIG{'PIPE'} = $SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";

# Write current message. EDATA
($sec, $min, $hour, $mday, $mon, $year, $wday) = localtime(time);
	$date = sprintf("%02d/%02d-%02d:%02d",$mon + 1, $mday, $hour, $min);

$sys_loginflg = $FORM{'TXTLOGIN'};
$sys_plyerno  = 0;
if ($FORM{'TXTPNO'} ne ''){
    $sys_plyerno  = $FORM{'TXTPNO'};
}
$sys_village = $FORM{'VILLAGENO'};
$sys_logviewflg = 0;
$sys_storytype = $FORM{'STORYTYPE'};

# FileName
$file_pdata = $dat_path.$sys_village.".dat";
$tmp_pdata  = $dat_path.$sys_village.".tmp";
$file_log   = $log_path.$sys_village.".dat";
$tmp_log    = $log_path.$sys_village.".tmp";

#cookie
if ($FORM{'COMMAND'} eq 'ENTER') {
    print &setCookie('SELECTROOM', $FORM{'VILLAGENO'});
}
if ($FORM{'COMMAND'} eq 'LOGIN') {
    print &setCookie('PLAYERNO'.$sys_village, $FORM{'CMBPLAYER'});
    print &setCookie('PASSWORD'.$sys_village, $FORM{'TXTPASS'});
}

print "Content-type: text/html\n";
print "\n";

# ***************************************************************** ログイン有無
if ($FORM{'TXTLOGIN'} ne '') {
    # =================================================================== 未ログイン 
    if ($sys_loginflg eq '1') {
        #--------------------------------------------------------------------- エントリー処理 
        if ($FORM{'COMMAND'} eq 'ENTRY') {
            $wk_entryflg = 0;
            if ($FORM{'TXTNAME'} ne '' && $FORM{'TXTPROFILE'} ne '' && $FORM{'TXTPASS'} ne '' && $FORM{'TXTHN'} ne '' && $FORM{'TXTMAIL'} ne '') {
                # READ
                open(IN, $file_pdata);
                $wk_count = 0;
                while (<IN>) {
                    $value = $_;
                    $value =~ s/\n//g;
                	$wk_count++;
                	if ($wk_count == 1){
                        @data_vildata = split(/,/, $value);
                        $data_no = $data_vildata[1];
                	}else{
                		$data_player[$wk_count-1] = $value;
                	}
                }
                close(IN);

                if ($data_vildata[0] >= 1) {
                    $wk_entryflg = 2;
                }elsif ($data_vildata[1] >= 22){
                    $wk_entryflg = 3;
                }else{
                    #WRITE
                    $data_no++;
                    # 0:NO , 1:ALIVE/DEAD , 2:VOTE , 3:JOB , 4:JOBwk , 5:WinLose , 6:COLOR , 7:PASSWORD , 8:NAME , 9:PROFILE , 10:HN , 11:silent , 12:mail , 13:date,
                    $data_player[$data_no] = $data_no.',A,0,NON,0,-,'.$FORM{'CMBCOLOR'}.','.$FORM{'TXTPASS'}.','.$FORM{'TXTNAME'}.','.$FORM{'TXTPROFILE'}.','.$FORM{'TXTHN'}.',0,'.$FORM{'TXTMAIL'}.','.$date;
                    open(OUT, "> ".$file_pdata);
                    $data_vildata[1] = $data_no;
                    # 0:GAMESTART , 1:PLAYERNO , 2:DATE , 3:FAZE , 4:TIME , 5:VILNAME , 6:FORMID
                    print OUT "$data_vildata[0],$data_vildata[1],$data_vildata[2],$data_vildata[3],$data_vildata[4],$data_vildata[5],$data_vildata[6]\n";
                	for ($i = 1; $i <= $data_no; $i++) {
                	    print OUT "$data_player[$i]\n";
                	}
                    close(OUT);
                    &msg_write(0, 1, 31,"「<b>$FORM{'TXTNAME'}</b>さん」が村へやってきました。");
                    $wk_entryflg = 1;
                }
            }
            # Print HTML document
            &disp_head1;
            print "<TR><TD>\n";
            if($wk_entryflg == 1){
                print "アナタは$data_no人目の村民として登録が完了しました。\n";
            }elsif($wk_entryflg == 2){
                print "申\し訳ありません。既にゲームが開始しています。\n";
            }elsif($wk_entryflg == 3){
                print "申\し訳ありません。既に２２名登録されています。\n";
            }else{
                print "入力項目が正しくありません。\n";
            }
            print "</TD></TR>\n";
        }
        #--------------------------------------------------------------------- ログイン処理
        if ($FORM{'COMMAND'} eq 'LOGIN') {
            $wk_loginflg = 0;
            $wk_count = 0;
            if ($FORM{'CMBPLAYER'} == 0){
                $wk_loginflg = 1;
                $sys_loginflg = '2';
                $sys_plyerno = 60;
    		}elsif ($FORM{'CMBPLAYER'} <= 22){
                open(IN, $file_pdata);
                while (<IN>) {
                	$wk_count++;
                	$value = $_;
                    $value =~ s/\n//g;
                    @wk_player = split(/,/, $value);
                	if ($wk_count > 1){
                		if ($wk_player[0] == $FORM{'CMBPLAYER'}){
                            if ($wk_player[7] eq $FORM{'TXTPASS'}){
                                $wk_loginflg = 1;
                                $sys_loginflg = '2';
                                $sys_plyerno = $FORM{'CMBPLAYER'};
                            }else{
                                $wk_loginflg = 9;
                            }
                		}
                	}
                }
                close(IN);
            }elsif ($FORM{'CMBPLAYER'} == 99){
                if ($FORM{'TXTPASS'} eq $sys_pass){
                    $wk_loginflg = 1;
                    $sys_loginflg = '2';
                    $sys_plyerno = 50;
                }else{
                    $wk_loginflg = 9;
                }
    		}
            # Print HTML document
            if($wk_loginflg != 1){
                &disp_head1;
                print "パスワードが正しくありません。\n";
            }
        }
        #--------------------------------------------------------------------- ログ閲覧
        if ($FORM{'COMMAND'} eq 'LOGVIEW') {
            $sys_loginflg = '2';
            $sys_plyerno = 60;
            $sys_logviewflg = 1;
        }
    }
    #=================================================================== ログインＯＫ
    if ($sys_loginflg eq '2') {

        # 現在の状態を確認
        open(IN, $file_pdata);
        $wk_count = 0;
        while (<IN>) {
            $value = $_;
            $value =~ s/\n//g;
        	$wk_count++;
        	if ($wk_count == 1){
        		@data_vildata = split(/,/, $value);
        	}else{
        		@wk_player = split(/,/, $value);
        		for ($i = 0; $i <= 13; $i++) {
            	    $data_player[$wk_count-1][$i] = $wk_player[$i];
            	}
           	}
        }
        close(IN);
        
        $wk_txtmsg1 = '';
        $wk_txtmsg2 = '';
        $wk_txtmsglen = 0;
        if ($FORM{'TXTMSG'} ne '') {
            $FORM{'TXTMSG'} =~ s/\r*$//g;
        	$FORM{'TXTMSG'} =~ s/\n//g;
        	$FORM{'TXTMSG'} =~ s/,//g;
            $wk_txtmsg1 = $FORM{'TXTMSG'};
            $wk_txtmsg2 = $FORM{'TXTMSG'};
        	$wk_txtmsg2 =~ s/\r/<BR>/g;
        	$wk_txtmsglen = length($FORM{'TXTMSG'});
        }

        $data_player[$sys_plyerno][13] = $date;

        #2重投稿防止
        if ($data_vildata[6] == $FORM{'FORMID'}) {
            $FORM{'COMMAND'} = '';
        }
        $data_vildata[6] = $FORM{'FORMID'};
        
        #=================================================================== 開始前
        if($data_vildata[0]==0){
            #--------------------------------------------------------------------- 開始
            if (($FORM{'COMMAND'} eq 'START' || $FORM{'COMMAND'} eq 'STARTF') && $data_vildata[1] >= 8) {
                #WRITE
                for ($i = 1; $i <= 22; $i++) {
            	    $wk_charactor[$i] = 'HUM';
            	}
            	$wk_charactor[1] = 'WLF';
            	$wk_charactor[2] = 'WLF';
            	$wk_charactor[3] = 'URA';
            	if($data_vildata[1] >= 16){
            	    $wk_charactor[4] = 'WLF';
            	}
            	if($data_vildata[1] >= 9){
            	    $wk_charactor[5] = 'NEC';
            	}
            	if($data_vildata[1] >= 10){
            	    $wk_charactor[6] = 'MAD';
            	}
            	if($data_vildata[1] >= 11){
            	    $wk_charactor[7] = 'BGD';
            	}
            	if($data_vildata[1] >= 13){
            	    $wk_charactor[8] = 'FRE';
            	    $wk_charactor[9] = 'FRE';
            	}
            	if($data_vildata[1] >= 15 && $FORM{'COMMAND'} eq 'STARTF'){
            	    $wk_charactor[10] = 'FOX';
            	}
                for ($i = 1; $i <= $data_vildata[1]; $i++) {
                    $wk_rnd = int(rand($data_vildata[1] - $i + 1)) + 1;
            	    $data_player[$i][3] = $wk_charactor[$wk_rnd];
            	    for ($i2 = $wk_rnd; $i2 <= $data_vildata[1]; $i2++) {
                        $wk_charactor[$i2] = $wk_charactor[$i2+1];
                	}
            	}
                $data_vildata[0] = 1;
                $data_vildata[2] = 1;
                $data_vildata[3] = 2;
                $data_vildata[4] = 24;
    
                # Print HTML document
                &msg_write(1, 50, 32,"<FONT size=\"+1\">１日目の夜となりました。</FONT>");
            }
            #--------------------------------------------------------------------- メッセージ
            if (($FORM{'COMMAND'} eq 'MSG' || $FORM{'COMMAND'} eq 'MSG2' || $FORM{'COMMAND'} eq 'MSG3') && $wk_txtmsg1 ne '') {
            	$wk_fonttag1 = "";
            	$wk_fonttag2 = "";

                # [ msg write ]
                if ($FORM{'COMMAND'} eq 'MSG2'){
                    $wk_fonttag1 = "<FONT size=\"+1\">";
                    $wk_fonttag2 = "</FONT>";
                }
                if ($FORM{'COMMAND'} eq 'MSG3'){
                    $wk_fonttag1 = "<FONT size=\"-1\">";
                    $wk_fonttag2 = "</FONT>";
                }
                &msg_write(0, 1, $sys_plyerno, $wk_fonttag1.$wk_txtmsg2.$wk_fonttag2);
            }
            #--------------------------------------------------------------------- 名前変更
            if ($FORM{'COMMAND'} eq 'NAMECHG' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 20){
                    $data_player[$sys_plyerno][8] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- プロフィール変更
            if ($FORM{'COMMAND'} eq 'PROFILE' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 80){
                    $data_player[$sys_plyerno][9] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- 村名変更
            if ($FORM{'COMMAND'} eq 'VILNAME' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 16){
                    $data_vildata[5] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- 管理者メッセージ
            if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                # [ msg write ]
                &msg_write(0, 1, 23, $wk_txtmsg2);
            }
        }
        #=================================================================== ＯＮＰＬＡＹ！
        if($data_vildata[0]==1){
            #--------------------------------------------------------------------- [ 昼 ]
            if($data_vildata[3]==1){
                #--------------------------------------------------------------------- メッセージ
                if (($FORM{'COMMAND'} eq 'MSG' || $FORM{'COMMAND'} eq 'MSG2' || $FORM{'COMMAND'} eq 'MSG3') && $wk_txtmsg1 ne '' && $data_vildata[4] < 48) {
                    if ($wk_txtmsglen <= 100){
                        $data_vildata[4] += 1;
                    }elsif ($wk_txtmsglen <= 200){
                        $data_vildata[4] += 2;
                    }elsif ($wk_txtmsglen <= 300){
                        $data_vildata[4] += 3;
                    }elsif ($wk_txtmsglen <= 400){
                        $data_vildata[4] += 4;
                    }elsif ($wk_txtmsglen <= 500){
                        $data_vildata[4] += 5;
                    }elsif ($wk_txtmsglen <= 600){
                        $data_vildata[4] += 6;
                    }elsif ($wk_txtmsglen <= 700){
                        $data_vildata[4] += 7;
                    }else{
                        $data_vildata[4] += 8;
                    }
                    if ($data_vildata[4] >= 48){
                        $data_vildata[4] = 48;
                    }

                    $wk_fonttag1 = "";
            	    $wk_fonttag2 = "";
                    # [ msg write ]
                    if ($FORM{'COMMAND'} eq 'MSG2'){
                        $wk_fonttag1 = "<FONT size=\"+1\">";
                        $wk_fonttag2 = "</FONT>";
                    }
                    if ($FORM{'COMMAND'} eq 'MSG3'){
                        $wk_fonttag1 = "<FONT size=\"-1\">";
                        $wk_fonttag2 = "</FONT>";
                    }
                    &msg_write($data_vildata[2], 1, $sys_plyerno, $wk_fonttag1.$wk_txtmsg2.$wk_fonttag2);
                }
                #--------------------------------------------------------------------- 霊 話
                if ($FORM{'COMMAND'} eq 'MSG0' && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, $sys_plyerno, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write($data_vildata[2], 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'MSGM0'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- 沈黙
                if ($FORM{'COMMAND'} eq 'SILENT') {
                    $data_player[$sys_plyerno][11] = 1;
                    # 判定
                    $wk_cnt_live   = 0;
                    $wk_cnt_silent = 0;
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        if ($data_player[$i][1] eq 'A'){
                            $wk_cnt_live++;
                            if ($data_player[$i][11] == 1) {
                                $wk_cnt_silent++;
                            }
                        }
                    }
                    # 半数 判定
                    if(int($wk_cnt_live / 2) < $wk_cnt_silent){
                        $data_vildata[4] += 4;
                        if ($data_vildata[4] >= 48){
                            $data_vildata[4] = 48;
                        }
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            $data_player[$i][11] = 0;
                        }
                        &msg_write($data_vildata[2], 1, 24, '「・・・・・・。」１時間ほどの沈黙が続いた。');
                    }
                }
                #--------------------------------------------------------------------- 投票
                if (($FORM{'COMMAND'} eq 'VOTE' && $data_player[$sys_plyerno][2] == 0 && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') || $FORM{'COMMAND'} eq 'VOTECHK') {
                	if ($FORM{'COMMAND'} eq 'VOTE'){
                	    $data_player[$sys_plyerno][2] = $FORM{'CMBPLAYER'};
                	}
                    # 投票判定
                    $wk_voteflg = 1;
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        $wk_votecount[$i] = 0;
                    }
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        if ($data_player[$i][2] != 0 && $data_player[$i][1] eq 'A'){
                            $wk_votecount[$data_player[$i][2]]++;
                        }
                        if ($data_player[$i][2] == 0 && $data_player[$i][1] eq 'A') {
                            $wk_voteflg = 0;
                        }
                    }

                    if ($wk_voteflg == 1){
                        $wk_topvote = 1;
                        $wk_votetable = "<TABLE>";
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            if ($data_player[$i][1] eq 'A'){
                                $wk_votetable = $wk_votetable."<TR><TD><b>$data_player[$i][8]</b>さん</TD><TD>$wk_votecount[$i] 票</TD><TD>投票先 → <b>$data_player[$data_player[$i][2]][8]</b>さん</TD></TR>";
                                if ($wk_votecount[$wk_topvote] < $wk_votecount[$i]){
                                    $wk_topvote = $i;
                                }
                            }
                        }
                        $wk_votetable = $wk_votetable."</TABLE>";
                        &msg_write($data_vildata[2], 2, 0,"$wk_votetable");
                        &msg_write($data_vildata[2], 2, 0,"<BR><FONT size=\"+1\">$data_vildata[2]日目 投票結果。</FONT>");
                        $wk_topvotecheck = 0;
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            if ($wk_votecount[$wk_topvote] == $wk_votecount[$i]){
                                $wk_topvotecheck++;
                            }
                        }
                        if ($wk_topvotecheck == 1){
                            # 投票終了
                            $data_vildata[3] = 2;
                            $data_vildata[4] = 24;
                            $data_player[$wk_topvote][1] = 'D';
                            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                                $data_player[$i][2] = 0;
                                $data_player[$i][11] = 0;
                                if ($data_player[$i][3] eq 'NEC' && $data_player[$i][1] eq 'A' && $data_vildata[2]>=2) {
                                    $data_player[$i][4] = $wk_topvote;
                                }
                                if ($data_player[$i][3] eq 'URA') {
                                    $data_player[$i][4] = 0;
                                }
                            }

                            # [ 勝利判定 ]
                            &sub_judge;
                            
                            if ($data_vildata[0] == 1) {
                                &msg_write($data_vildata[2], 2, 33,"<b>$data_player[$wk_topvote][8]</b>さんは村民協議の結果<FONT color=\"#ff0000\">処刑されました・・・。</FONT>");
                                &msg_write($data_vildata[2], 50, 32,"<FONT size=\"+1\">$data_vildata[2]日目の夜となりました。</FONT>");
                            }
                        }else{
                            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                                $data_player[$i][2] = 0;
                            }
                            &msg_write($data_vildata[2], 2, 31,"<FONT size=\"+1\">再投票となりました。</FONT>");
                        }
                    }
                }
                #--------------------------------------------------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'SHOCK' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$FORM{'CMBPLAYER'}][1] = 'D';
                    &msg_write($data_vildata[2], 1, 34,"<b>$data_player[$FORM{'CMBPLAYER'}][8]</b>さんは都合により<FONT color=\"#ff0000\">突然死しました・・・。</FONT>");
                }
            }
            #--------------------------------------------------------------------- [ 夜 ]
            if($data_vildata[3] == 2){
                #-------------------------- 遠吠え
                if ($FORM{'COMMAND'} eq 'MSGWLF' && $wk_txtmsg1 ne '' && $data_vildata[4] < 48) {
                    if ($wk_txtmsglen <= 100){
                        $data_vildata[4] += 1;
                    }elsif ($wk_txtmsglen <= 200){
                        $data_vildata[4] += 2;
                    }elsif ($wk_txtmsglen <= 300){
                        $data_vildata[4] += 3;
                    }else{
                        $data_vildata[4] += 4;
                    }
                    if ($data_vildata[4] >= 48){
                        $data_vildata[4] = 48;
                    }
                    # [ msg write ]
                    &msg_write($data_vildata[2], 3, $sys_plyerno, $wk_txtmsg2);
                }
                #-------------------------- 殺害予告
                if ($FORM{'COMMAND'} eq 'KILL' && $data_player[$FORM{'CMBPLAYER'}][3] ne 'WLF' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        if ($data_player[$i][3] eq 'WLF') {
                            $data_player[$i][4] = $FORM{'CMBPLAYER'};
                            #&msg_write($data_vildata[2], 11, 42,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>さんを狙います。</FONT>");
                        }
                    }
                    &msg_write($data_vildata[2], 11, 42,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>さんを狙います。");
                }
                #-------------------------- 占い師
                if ($FORM{'COMMAND'} eq 'FORTUNE' && $data_player[$sys_plyerno][4] == 0 && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$sys_plyerno][4] = $FORM{'CMBPLAYER'};
                    &msg_write($data_vildata[2], 12, 43,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>さんを占います。");
                }
                #-------------------------- 狩人
                if ($FORM{'COMMAND'} eq 'GUARD' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$sys_plyerno][4] = $FORM{'CMBPLAYER'};
                    &msg_write($data_vildata[2], 13, 44,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>さんを護衛します。");
                }
                
                #--------------------------- 霊 話
                if ($FORM{'COMMAND'} eq 'MSG0' && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, $sys_plyerno, $wk_txtmsg2);
                }
                #--------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write($data_vildata[2], 2, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'MSGM0'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- 夜終了判定
                if ($FORM{'COMMAND'} ne '') {
                    $wk_nightend = 1;
                    $wk_targetwlf = 0;
                    $wk_targetura = 0;
                    $wk_targetbgd = 0;
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        if ($data_player[$i][1] eq 'A') {
                            if ($data_player[$i][3] eq 'WLF'){
                                $wk_targetwlf = $data_player[$i][4];
                                if ($data_player[$i][4] == 0) {
                                    $wk_nightend = 0;
                                }
                            }
                            if ($data_player[$i][3] eq 'URA') {
                                $wk_targetura = $data_player[$i][4];
                                if ($data_player[$i][4] == 0) {
                                    $wk_nightend = 0;
                                }
                            }
                            if ($data_player[$i][3] eq 'BGD' && $data_vildata[2] >= 2) {
                                $wk_targetbgd = $data_player[$i][4];
                                if ($data_player[$i][4] == 0) {
                                    $wk_nightend = 0;
                                }
                            }
                        }
                    }
                    if ($wk_nightend == 1) {
                        $wk_alivewlf = 0;
                        $wk_alivehum = 0;
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            if ($data_player[$i][1] eq 'A'){
                                if ($data_player[$i][3] eq 'WLF'){
                                    $wk_alivewlf++;
                                }else{
                                    $wk_alivehum++;
                                }
                            }
                        }
                        
                        # 護衛、妖狐判定
                        if ($wk_targetwlf != $wk_targetbgd && $data_player[$wk_targetwlf][3] ne 'FOX') {
                            $data_player[$wk_targetwlf][1] = 'D';
                            &msg_write($data_vildata[2], 4, 34,"<b>$data_player[$wk_targetwlf][8]</b>さんは翌日<FONT color=\"#ff0000\">無残な姿で発見された・・・。</FONT>");
                        }
                        if ($data_player[$wk_targetura][3] eq 'FOX') {
                            $data_player[$wk_targetura][1] = 'D';
                            &msg_write($data_vildata[2], 4, 34,"<b>$data_player[$wk_targetura][8]</b>さんは翌日<FONT color=\"#ff0000\">無残な姿で発見された・・・。</FONT>");
                        }

                        # [ 勝利判定 ]
                        &sub_judge;
                        
                        if ($data_vildata[0] == 1) {
                            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                                if ($data_player[$i][3] eq 'WLF') {
                                    $data_player[$i][4] = 0;
                                }
                                if ($data_player[$i][3] eq 'BGD') {
                                    $data_player[$i][4] = 0;
                                }
                            }
                            $data_vildata[2]++;
                            $data_vildata[3] = 1;
                            $data_vildata[4] = 0;
                            &msg_write($data_vildata[2], 50, 32,"<FONT size=\"+1\">$data_vildata[2]日目の朝となりました。</FONT>");
                        }
                    }
                }
                #--------------------------------------------------------------------- 管理者メッセージ
                if ($FORM{'COMMAND'} eq 'SHOCK' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$FORM{'CMBPLAYER'}][1] = 'D';
                    &msg_write($data_vildata[2], 2, 34,"<b>$data_player[$FORM{'CMBPLAYER'}][8]</b>さんは都合により<FONT color=\"#ff0000\">突然死しました・・・。</FONT>");
                }
            }
        }
        #=================================================================== ゲーム終了
        if($data_vildata[0]==2){
            #--------------------------------------------------------------------- メッセージ
            if (($FORM{'COMMAND'} eq 'MSG' || $FORM{'COMMAND'} eq 'MSG2' || $FORM{'COMMAND'} eq 'MSG3') && $wk_txtmsg1 ne '' && $data_vildata[4] < 48) {
                $wk_fonttag1 = "";
        	    $wk_fonttag2 = "";
                # [ msg write ]
                if ($FORM{'COMMAND'} eq 'MSG2'){
                    $wk_fonttag1 = "<FONT size=\"+1\">";
                    $wk_fonttag2 = "</FONT>";
                }
                if ($FORM{'COMMAND'} eq 'MSG3'){
                    $wk_fonttag1 = "<FONT size=\"-1\">";
                    $wk_fonttag2 = "</FONT>";
                }
                &msg_write($data_vildata[2], 1, $sys_plyerno, $wk_fonttag1.$wk_txtmsg2.$wk_fonttag2);
            }
            #--------------------------------------------------------------------- 管理者メッセージ
            if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                # [ msg write ]
                &msg_write($data_vildata[2], 50, 23,$wk_txtmsg2);
            }
        }

        # 0:GAMESTART , 1:PLAYERNO , 2:DATE , 3:FAZE , 4:TIME , 5:FORMID
        # 0:NO , 1:ALIVE/DEAD , 2:VOTE , 3:JOB , 4:JOBwk , 5:wk1 , 6:wk2 , 7:PASSWORD , 8:NAME , 9:PROFILE 
        
        # [ HEAD ]
        &disp_head2;

        # [ PLAYER LIST ]
        &disp_players;

        # [ MY DATA ]
        &disp_mydata;
        
        if ($sys_logviewflg != 1 || $sys_storytype != "2"){
            print "<TR><TD class=\"CLSTD01\">◆ 出来事</TD></TR>\n";
            print "<TR><TD>\n";
            # [ 日付 ]
            &disp_time(@data_vildata);
            print "<BR>\n";
            # [ コメント ]
            &disp_msg;
            print "</TD></TR>\n";
        }
        
        # [ 行動設定 ]
        &disp_command;

        # [ コメントdead ]
        &disp_msgdead;

        
        #データ書きこみ
        if($sys_plyerno <= 50){
            &data_write;
        }
    }
    
    print "</TD></TR>\n";
    print "<TR><TD class=\"CLSTD01\"><A href=\"$return_url\">戻る</A>\n";
    print "<INPUT type=\"hidden\" name=\"TXTPNO\" value=\"$sys_plyerno\">";
    print "<INPUT type=\"hidden\" name=\"VILLAGENO\" value=\"$sys_village\">";
    print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"2\">";
    $wk_rnd = int(rand(1000000)) + 1;
    print "<INPUT type=\"hidden\" name=\"FORMID\" value=\"$wk_rnd\">";
    print "</TD></TR>\n";
}
# ***************************************************************** ログインなし
else{
    &disp_head1;
    if ($FORM{'TXTPASS'} eq $sys_pass) {
        if ($FORM{'COMMAND'} eq 'NEWVILLAGE') {
            $wk_fileno = 1;
            while (open(IN, $dat_path.$wk_fileno.".dat")) {
                $wk_fileno++;
                close(IN);
            }
        
            $file_pdata = $dat_path.$wk_fileno.".dat";
            $file_log   = $log_path.$wk_fileno.".dat";
            @data_vildata = (0,0,0,1,0,'どこかの');
        
            &data_write;
            open(OUT, "> ".$file_log);
            close(OUT);
        
            print "<TR><TD align=\"center\">新規に作成しました。</TD></TR>\n";
        } elsif ($FORM{'COMMAND'} eq 'DELVILLAGE') {
            open(IN, $dat_path.$sys_village.".dat");
            @wk_vildata = split(/,/,<IN>);
            close(IN);
            if ($wk_vildata[0] == 2) {
                $file_pdata = $dat_path.$sys_village.".dat";
                unlink($file_pdata);
                $file_log   = $log_path.$sys_village.".dat";
                unlink($file_log);
                print "<TR><TD align=\"center\">村 $sys_village番を削除しました。</TD></TR>\n";
            } else {
                print "<TR><TD align=\"center\">ゲームを終了してから削除してください。</TD></TR>\n";
            }
        } elsif ($FORM{'COMMAND'} eq 'ENDVILLAGE') {
            open(IN, $file_pdata);
            $wk_count = 0;
            while (<IN>) {
                $value = $_;
                $value =~ s/\n//g;
            	$wk_count++;
            	if ($wk_count == 1){
            		@data_vildata = split(/,/, $value);
            	}else{
            		@wk_player = split(/,/, $value);
            		for ($i = 0; $i <= 13; $i++) {
                	    $data_player[$wk_count-1][$i] = $wk_player[$i];
                	}
               	}
            }
            close(IN);
            
            $data_vildata[0] = 2;
            &data_write;
            print "<TR><TD align=\"center\">村 $sys_village番ゲームを強制終了しました。</TD></TR>\n";
        }
        &disp_admin;
    } else {
        if ($FORM{'COMMAND'} eq 'ENTER') {
            &disp_login;
        }else{
            if ($ARGV[0] eq "room") {
                &disp_room;
            }
            elsif ($ARGV[0] eq "entry") {
                &disp_entry;
            }
            elsif ($ARGV[0] eq "log") {
                &disp_logview;
            }
            elsif ($ARGV[0] eq "master") {
                &disp_admin;
            }
            else {
                print "<TR><TD align=\"center\">正しい入り口からどうぞ。</TD></TR>\n";
            }
        }
    }
}

# [ FOOT ]
&disp_foot;

# Lock解除
rmdir($lock_path);

##########################################################################################################
# サブルーチン
##########################################################################################################
#---------------------------------------------------------------------
sub data_write{
    open(OUT, "> ".$file_pdata);
    print OUT "$data_vildata[0],$data_vildata[1],$data_vildata[2],$data_vildata[3],$data_vildata[4],$data_vildata[5],$data_vildata[6]\n";
	for ($i9 = 1; $i9 <= $data_vildata[1]; $i9++) {
	    print OUT "$data_player[$i9][0],$data_player[$i9][1],$data_player[$i9][2],$data_player[$i9][3],$data_player[$i9][4],$data_player[$i9][5],$data_player[$i9][6],$data_player[$i9][7],$data_player[$i9][8],$data_player[$i9][9],$data_player[$i9][10],$data_player[$i9][11],$data_player[$i9][12],$data_player[$i9][13]\n";
	}
    close(OUT);
}
#---------------------------------------------------------------------
sub msg_write{
    @wk_writedata = @_;
    open(OUT, "> ".$tmp_log);
	open(IN, $file_log);
    print OUT "$wk_writedata[0],$wk_writedata[1],$wk_writedata[2],$wk_writedata[3]\n";
	while (<IN>) {
		print OUT;
	}
	close(IN);
	close(OUT);

	# Copy .tmp to .dat
	open(IN, $tmp_log);
	open(OUT, "> ".$file_log);
	$msgs = 0;
	while (<IN>) {
		# if ($msgs++ >= 2000) { last; }
		print OUT;
	}
	close(IN);
	close(OUT);
	unlink($tmp_log);
}
#---------------------------------------------------------------------
sub disp_head1{
    print "<HTML>\n";
    print "<HEAD>\n";
    print "<TITLE>$sys_title</TITLE>\n";
    print "</HEAD>\n";
    print "<BODY>\n";
    print "<FORM action=\"$cgi_path\" method=\"POST\">\n";
    print "<TABLE width=\"700\" cellspacing=\"5\"><TBODY>\n";
}
#---------------------------------------------------------------------
sub disp_room{
    # Cookieの値を得る
    &getCookie();
    $sys_default0 = $COOKIE{'SELECTROOM'};
    if ($sys_default0 eq "") {
        $sys_default0 = 0;
    }
    
    print "<TR><TD>\n";
    print "<TABLE>\n";
    
    print "<TR><TD>村を選択</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        @wk_vildata = split(/,/,<IN>);
        print "<OPTION value=\"$wk_fileno\" ";
        if ($sys_default0 == $wk_fileno) {
            print "selected";
        }
        print ">村 住所$wk_fileno番 $wk_vildata[5]村</OPTION>\n";
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";

    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"村に行く\"></TD></TR>\n";
    print "</TABLE>\n";
    #print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"\">\n";
    print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"ENTER\">\n";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_login{
    # Cookieの値を得る
    &getCookie();
    $sys_default1 = $COOKIE{'PLAYERNO'.$sys_village};
    if ($sys_default1 eq "") {
        $sys_default1 = 0;
    }
    $sys_default2 = $COOKIE{'PASSWORD'.$sys_village};
    
    print "<TR><TD>\n";
    print "<TABLE>\n";

    open(IN, $file_pdata);
    @wk_vildata = split(/,/, <IN>);
    print "<TR><TD>村を選択</TD><TD>村 住所$sys_village番 $wk_vildata[5]村</TD></TR>\n";
    print "<TR><TD>名前を選択</TD><TD><SELECT name=\"CMBPLAYER\">\n";
    print "<OPTION value=\"0\">旅　人（観戦）</OPTION>\n";
    while ($value = <IN>) {
        $value =~ s/\n//g;
		@wk_player = split(/,/, $value);
        print "<OPTION value=\"$wk_player[0]\"";
        if ($sys_default1 == $wk_player[0]) {
            print " selected";
        }
        print ">$wk_player[8]</OPTION>\n";
    }
    close(IN);
    print "<OPTION value=\"99\"";
    if ($sys_default1 == 99) {
        print " selected";
    }
    print ">管理者</OPTION>\n";
    print "</SELECT></TD></TR>\n";
    
    print "<TR><TD>パスワード</TD><TD><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\" value=\"$sys_default2\"></TD></TR>\n";
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"村に行く\"></TD></TR>\n";
    print "</TABLE>\n";
    print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"1\">\n";
    print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"LOGIN\">\n";
    print "<INPUT type=\"hidden\" name=\"VILLAGENO\" value=\"$sys_village\">";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_admin{
    print "<TR><TD>\n";
    print "<TABLE>\n";

    print "<TR><TD>村を選択</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        print "<OPTION value=\"$wk_fileno\">村 住所 $wk_fileno番</OPTION>\n";
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";
    
    print "<TR><TD>新規NO</TD><TD>村NO $wk_fileno</TD></TR>";
    
    print "<TR><TD>処理選択</TD><TD><SELECT name=\"COMMAND\">\n";
    print "  <OPTION value=\"NEWVILLAGE\">村を作成</OPTION>\n";
    print "  <OPTION value=\"DELVILLAGE\">村の削除</OPTION>\n";
    print "  <OPTION value=\"ENDVILLAGE\">ゲームの強制終了</OPTION>\n";
    print "</SELECT></TD></TR>\n";

    print "<TR><TD>パスワード</TD><TD><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\"></TD></TR>\n";
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"処理実行\"></TD></TR>\n";
    print "</TABLE>\n";
    #print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"1\">\n";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_entry{
    $wk_fileno = 1;
    $wk_entryflg = 0;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        @wk_vildata = split(/,/,<IN>);
        if ($wk_vildata[0] == 0) {
            $wk_entryflg = 1;
        }
        $wk_fileno++;
        close(IN);
    }
    print "<TR><TD>\n";
    if ($wk_entryflg == 1) {
        print "<CENTER><BR><TABLE border=\"1\" cellspacing=\"4\"><TBODY><TR><TD>";
        print "<TABLE cellpadding=\"4\"><TBODY>";
    
        print "<TR><TD align=\"center\"><B><FONT size=\"+2\">村民登録書</FONT></B></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";
    
        print "<TR><TD align=\"center\">◆村を選択してください。</TD></TR>\n";
        print "<TR><TD align=\"center\"><SELECT name=\"VILLAGENO\">\n";
        $wk_fileno = 1;
        while (open(IN, $dat_path.$wk_fileno.".dat")) {
            @wk_vildata = split(/,/,<IN>);
            if ($wk_vildata[0] == 0) {
                print "<OPTION value=\"$wk_fileno\">村 住所$wk_fileno番 $wk_vildata[5]村</OPTION>\n";
            }
            $wk_fileno++;
            close(IN);
        }
        print "  </SELECT></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";
    
        print "<TR><TD align=\"center\">◆アナタのHNを入力してください。（10文字）</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"20\" maxlength=\"10\" type=\"text\" name=\"TXTHN\"></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";
    
        print "<TR><TD align=\"center\">◆アナタの表\示色を選択してください。</TD></TR>\n";
        print "<TR><TD align=\"center\"><SELECT name=\"CMBCOLOR\">\n";
        print "<OPTION value=\"1\" selected>明灰 lightglay</OPTION>\n";
        print "<OPTION value=\"2\">暗灰 darkglay</OPTION>\n";
        print "<OPTION value=\"3\">黄 yellow</OPTION>\n";
        print "<OPTION value=\"4\">橙 orange</OPTION>\n";
        print "<OPTION value=\"5\">赤 red</OPTION>\n";
        print "<OPTION value=\"6\">水 lightblue</OPTION>\n";
        print "<OPTION value=\"7\">青 blue</OPTION>\n";
        print "<OPTION value=\"8\">緑 green</OPTION>\n";
        print "<OPTION value=\"9\">紫 purple</OPTION>\n";
        print "<OPTION value=\"10\">桃 pink</OPTION>\n";
        print "</SELECT></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";

        print "<TR><TD align=\"center\">◆アナタの村人としての名前を入力してください。（10文字）<BR>（例：山田　人郎）<BR><FONT size=\"-1\">プレイ中はこの名前を使用します。HNがばれないものが好ましいです。</FONT></TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"20\" maxlength=\"10\" type=\"text\" name=\"TXTNAME\"></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";

        print "<TR><TD align=\"center\">◆アナタの村人プロフィールを書いてください。（40文字）<BR>（例：４０歳・自営業・村の指相撲チャンプ・現在２連覇）</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"60\" maxlength=\"40\" type=\"text\" name=\"TXTPROFILE\"></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";

        print "<TR><TD align=\"center\">◆アナタのログインパスワードを入力してください。（半角英数字4文字）<BR>（他のプレイヤーに解らないようなものにしてください。）</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\"></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";

        print "<TR><TD align=\"center\">◆メールアドレスを入力してください。<BR>（連絡用に使用します。）</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"40\" type=\"text\" name=\"TXTMAIL\"></TD></TR>\n";
        print "<TR><TD align=\"center\">◇</TD></TR>\n";

        print "<TR><TD align=\"center\">「村民約定」<BR>私は村のため家族のためにそして自分自身のために<BR>もしかしたら、たまたま、いや、なんとなく、現れるかもしれない<BR>「人狼」と戦い抜くことを誓います。</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT type=\"submit\" value=\"同意する（登録）\"></TD></TR>\n";
    
        print "</TBODY></TABLE>\n";
        print "</TD></TR></TBODY></TABLE></CENTER>\n";
        print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"1\">";
        print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"ENTRY\">\n";
    } else {
        print "滞在可能\な村がありませんでした。";
    }
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_logview{
    # Cookieの値を得る
    &getCookie();
    $sys_default0 = $COOKIE{'SELECTROOM'};
    if ($sys_default0 eq "") {
        $sys_default0 = 0;
    }
    
    print "<TR><TD>\n";
    print "<TABLE>\n";
    
    print "<TR><TD>村を選択</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        @wk_vildata = split(/,/,<IN>);
        if ($wk_vildata[0] == 2) {
            print "<OPTION value=\"$wk_fileno\" ";
            if ($sys_default0 == $wk_fileno) {
                print "selected";
            }
            print ">村 住所$wk_fileno番 $wk_vildata[5]村</OPTION>\n";
        }
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";

    print "<TR><TD>話を選択</TD><TD><SELECT name=\"STORYTYPE\">\n";
    print "<OPTION value=\"1\" selected>村人の戦い</OPTION>\n";
    print "<OPTION value=\"2\">霊の談話</OPTION>\n";
    print "</SELECT></TD></TR>\n";
    
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"記録を見る\"></TD></TR>\n";
    print "</TABLE>\n";
    print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"1\">\n";
    print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"LOGVIEW\">\n";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_head2{
    print "<HTML>\n";
    print "<HEAD>\n";
    print "<STYLE type=\"text/css\"><!--\n";
    print "TABLE{ font-size : 11pt; }\n";
    print ".CLSTABLE{ font-size : 10pt; }\n";
    print ".CLSTABLE2{ color : #333333; }\n";
    if ($data_vildata[3] == 1) {
        print ".CLSTD01{ color : white; background-color : black; font-weight : bold; }\n";
    }
    if ($data_vildata[3] == 2) {
        print ".CLSTD01{ color : black; background-color : white; font-weight : bold; }\n";
    }
    print ".CLSTD02{ background-color : #e3e3e3; }\n";
    print "--></STYLE>\n";
    print "<TITLE>$sys_title</TITLE>\n";
    print "</HEAD>\n";
    if ($data_vildata[3] == 1) {
        print "<BODY link=\"#FFCC00\" vlink=\"#FFCC00\" alink=\"#FFCC00\">\n";
    }
    if ($data_vildata[3] == 2) {
        print "<BODY bgcolor=\"#000000\" text=\"#ffffff\" link=\"#FF6600\" vlink=\"#FF6600\" alink=\"#FF6600\">\n";
    }
    print "<FORM action=\"$cgi_path\" method=\"POST\">\n";
    print "<TABLE width=\"700\" cellspacing=\"5\"><TBODY>\n";
    print "<TR><TD height=\"80\"><FONT size=\"+3\">$sys_title</FONT></TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_players{
    print "<TR><TD class=\"CLSTD01\">◆ 村人たち</TD></TR>\n";
    print "<TR><TD><TABLE class=\"CLSTABLE\"><TBODY>\n";
    $wk_amari = (5 - ($data_vildata[1] % 5)) % 5;
    $wk_iend  = $data_vildata[1] + $wk_amari;
    for ($i = 1; $i <= $wk_iend; $i++) {
        if ($i % 5 == 1){
            print "<TR>";
        }
	    if ($i <= $data_vildata[1]){
	        if ($data_player[$i][1] eq 'A'){
                print "<TD valign=\"top\"><IMG src=\"".$imgpath."alive".$data_player[$i][6].".gif\" title=\"$data_player[$i][9]\" alt=\"$data_player[$i][9]\" width=\"32\" height=\"32\" border=\"0\"></TD>\n";
            }
            if ($data_player[$i][1] eq 'D'){
                print "<TD valign=\"top\"><IMG src=\"".$imgpath."grave.gif\" title=\"$data_player[$i][9]\" width=\"32\" height=\"32\" border=\"0\"></TD>\n";
            }
            print "<TD>$data_player[$i][8]<BR>";
            if ($data_vildata[0] == 2 || $data_player[$sys_plyerno][1] eq 'D' || $sys_plyerno == 50) {
                print "<b>$data_player[$i][10]</b>さん<BR>";
                if ($data_player[$i][3] eq 'HUM') {
                    print "[$chr_hum]";
                }
                if ($data_player[$i][3] eq 'WLF') {
                    print "[$chr_wlf]";
                }
                if ($data_player[$i][3] eq 'URA') {
                    print "[$chr_ura]";
                }
                if ($data_player[$i][3] eq 'NEC') {
                    print "[$chr_nec]";
                }
                if ($data_player[$i][3] eq 'MAD') {
                    print "[$chr_mad]";
                }
                if ($data_player[$i][3] eq 'BGD') {
                    print "[$chr_bgd]";
                }
                if ($data_player[$i][3] eq 'FRE') {
                    print "[$chr_fre]";
                }
                if ($data_player[$i][3] eq 'FOX') {
                    print "[$chr_fox]";
                }
                if ($sys_plyerno == 50) {
                    print "<A href=\"mailto:$data_player[$i][12]\?Subject=お知らせ\">◆</A>";
                    if ($data_player[$i][2] != 0) {
                        print "<FONT color=\"0000FF\">◆</FONT>";
                    }
                    if ($data_player[$i][4] != 0) {
                        print "<FONT color=\"00FF00\">◆</FONT>";
                    }
                    print "<BR>$data_player[$i][13]";
                }
                print "<BR>";
            }
            if ($data_player[$i][1] eq 'A'){
                print "（生存中）</TD>\n";
            }
            if ($data_player[$i][1] eq 'D'){
                print "（死　亡）</TD>\n";
            }
    	}else{
    	    print OUT "<TD></TD><TD></TD>\n";
    	}
	    if ($i % 5 == 0){
            print "</TR>";
        }
	}
    print "</TBODY></TABLE></TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_mydata{
    if($data_vildata[0] == 1 && $sys_plyerno <= 22){
        print "<TR><TD class=\"CLSTD01\">◆ アナタの情報</TD></TR>\n";
        if ($data_player[$sys_plyerno][1] eq 'A') {
            print "<TR><TD><TABLE cellspacing=\"0\"><TBODY>\n";
            if ($data_player[$sys_plyerno][3] eq 'HUM') {
                print "<TR><TD><IMG src=\"".$imgpath."hum.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_hum」です。<BR>";
                print "【能\力】ありません。しかし、アナタの知恵と勇気で村を救うことができるはずです。</TD></TR>";
            }
            if ($data_player[$sys_plyerno][3] eq 'WLF') {
                print "<TR><TD><IMG src=\"".$imgpath."wlf.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_wlf」です。<BR>";
                print "【能\力】夜の間に他の人狼と協力し村人ひとり殺害できます。アナタはその強力な力で村人を食い殺すのです。</TD></TR>";
                for ($i = 1; $i <= $data_vildata[1]; $i++) {
        	        if ($data_player[$i][3] eq 'WLF' && $i != $sys_plyerno) {
        	            print "<TR><TD colspan=\"2\">【能\力発動】誇り高き人狼の血を引く仲間は<b>$data_player[$i][8]</b>さんです。</TD></TR>";
        	        }
            	}
            	if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">【能\力発動】アナタは<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>さんを殺る予\定です。</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'URA') {
                print "<TR><TD><IMG src=\"".$imgpath."ura.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_ura」です。<BR>";
                print "【能\力】夜の間に村人ひとりを「人」か「狼」か調べることができます。アナタが村人の勝利を握っています。</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">【能\力発動】占いの結果、<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>さんは";
                    if ($data_player[$data_player[$sys_plyerno][4]][3] eq 'WLF') {
                        print "「$chr_wlf」でした。"
                    }else{
                        print "「$chr_hum」でした。"
                    }
                    print "</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'NEC') {
                print "<TR><TD><IMG src=\"".$imgpath."nec.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_nec」です。<BR>";
                print "【能\力】[２日目以降]その日のリンチ死者が「人」か「狼」か調べることができます。地味ですがアナタの努力次第で大きく貢献することも不可能\ではありません。</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">【能\力発動】前日処刑された<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>さんは";
                    if ($data_player[$data_player[$sys_plyerno][4]][3] eq 'WLF') {
                        print "「$chr_wlf」でした。"
                    }else{
                        print "「$chr_hum」でした。"
                    }
                    print "</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'MAD') {
                print "<TR><TD><IMG src=\"".$imgpath."mad.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_mad」です。<BR>";
                print "【能\力】人狼の勝利がアナタの勝利となります。アナタはできるかぎり狂って場をかき乱すのです。バカになれ。</TD></TR>";
            }
            if ($data_player[$sys_plyerno][3] eq 'BGD') {
                print "<TR><TD><IMG src=\"".$imgpath."bgd.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_bgd」です。<BR>";
                print "【能\力】[２日目以降]夜の間に村人ひとりを指定し人狼の殺害から護ることができます。人狼のココロを読むのです。</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">【能\力発動】アナタは<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>さんを護衛しています。</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'FRE') {
                print "<TR><TD><IMG src=\"".$imgpath."fre.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_fre」です。<BR>";
                print "【能\力】アナタはもうひとりの$chr_freがだれであるかを知ることができます。生存期間が他に比べ永い能\力です。アナタには推理する時間が与えられたのです。悩みなさい。</TD></TR>";
            	for ($i = 1; $i <= $data_vildata[1]; $i++) {
        	        if ($data_player[$i][3] eq 'FRE' && $i != $sys_plyerno) {
        	            print "<TR><TD colspan=\"2\">【能\力発動】もうひとりの$chr_freは<b>$data_player[$i][8]</b>さんです。</TD></TR>";
        	        }
            	}
            }
            if ($data_player[$sys_plyerno][3] eq 'FOX') {
                print "<TR><TD><IMG src=\"".$imgpath."fox.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>アナタの役割は「$chr_fox」です。<BR>";
                print "【能\力】アナタは人狼に殺されることはありません。ただし占われてしまうと死んでしまいます。村人を騙し、人狼を騙し、村を妖狐のものにするのです。</TD></TR>";
            }

            if ($data_player[$sys_plyerno][11] == 1) {
                print "<TR><TD colspan=\"2\">【沈　黙】アナタは他の様子を伺いながら沈黙しています。（発言はできます）</TD></TR>";
            }
            if ($data_player[$sys_plyerno][2] != 0) {
                print "<TR><TD colspan=\"2\">【投　票】アナタは<B>$data_player[$data_player[$sys_plyerno][2]][8]</B>さんに投票を行いました。</TD></TR>";
            }
            print "</TBODY></TABLE></TD></TR>\n";
        }else{
            print "<TR><TD>アナタは息絶えました・・・</TD></TR>\n";
        }
    }
    if($data_vildata[0] == 2 && $sys_plyerno <= 22) {
        print "<TR><TD class=\"CLSTD01\">◆ アナタの情報</TD></TR>\n";
        if ($data_player[$sys_plyerno][5] eq 'W') {
            print "<TR><TD>アナタは<FONT color=\"FF0000\">勝利</FONT>しました。</TD></TR>\n";
        }else{
            print "<TR><TD>アナタは<FONT color=\"0000FF\">敗北</FONT>しました。</TD></TR>\n";
        }
    }
}
#---------------------------------------------------------------------
sub disp_time{
    $wk_faze[0] = '';
    $wk_faze[1] = 'sun.gif';
    $wk_faze[2] = 'moon.gif';
    print "<IMG src=\"".$imgpath."village.gif\" width=\"32\" height=\"32\" border=\"0\"> ";
    print "<FONT size=\"+2\">～ $_[5]村 ～</FONT><BR>";
    print "<IMG src=\"".$imgpath."clock.gif\" width=\"32\" height=\"32\" border=\"0\"> ";
    if($_[2]==0){
        print "<FONT size=\"+2\">事件前日</FONT>";
    }else{
        print "<FONT size=\"+2\">$_[2]</FONT>日目 ";
        print "<IMG src=\"".$imgpath.$wk_faze[$_[3]]."\" border=\"0\"> ";
        # 昼
        if ($_[3]==1){
            if ($_[4] < 48){
                $wk_hour = int((48 - $_[4]) / 4);
                $wk_min = ((4 - ($_[4] % 4)) % 4) * 15;
                print "日没まであと <FONT size=\"+2\">$wk_hour</FONT>時間";
                if($wk_min > 0){
                    print " <FONT size=\"+2\">$wk_min</FONT>分";
                }
            }else{
                # 投票判定
                $wk_nonvotecount = 0;
                for ($i = 1; $i <= $data_vildata[1]; $i++) {
                    if ($data_player[$i][2] == 0 && $data_player[$i][1] eq 'A') {
                        $wk_nonvotecount++;
                    }
                }
                print "太陽が西の空に沈みかけています。<FONT size=\"+2\">投票</FONT>を行ってください。<BR>";
                print "あと<FONT size=\"+2\">$wk_nonvotecount</FONT>名の投票待ちとなっています。";
            }
        }
        # 夜
        if ($_[3]==2){
            if ($_[4] < 48){
                $wk_hour = int((48 - $_[4]) / 4);
                $wk_min = ((4 - ($_[4] % 4)) % 4) * 15;
                print "夜明けまであと <FONT size=\"+2\">$wk_hour</FONT>時間";
                if($wk_min > 0){
                    print " <FONT size=\"+2\">$wk_min</FONT>分";
                }
            }else{
                # 投票判定
                print "東の空が白みはじめています。<FONT size=\"+2\">能\力対象</FONT>を決定してください。<BR>";
            }
        }
        print "<BR>\n";
    }
}
#---------------------------------------------------------------------
sub disp_msg{
    $wk_inputflg = 0;
    print "<TABLE cellpadding=\"0\"><TBODY>";
    open(IN, $file_log);
    while ($wk_inputflg == 0) {
        if ($_ = <IN>){
            $wk_msgwriteflg = 0;
            @wk_logdata = split(/,/, $_);
            # 開始前
            if ($data_vildata[0] == 0){
                $wk_msgwriteflg = 1;
            }
            # ゲーム中、終了後ログイン
            if ($data_vildata[0] == 1 || ($data_vildata[0] == 2 && $sys_logviewflg == 0)){
                # 昼
                if ($data_vildata[3] == 1){
                    if ($wk_logdata[0] == $data_vildata[2] && ($wk_logdata[1] <= 2 || $wk_logdata[1] == 50)){
                    	$wk_msgwriteflg = 1;
                    }
                    if ($wk_logdata[0] == $data_vildata[2] - 1 && ($wk_logdata[1] == 2 || $wk_logdata[1] == 4)){
                    	$wk_msgwriteflg = 1;
                    }
                    if ($wk_logdata[0] <= $data_vildata[2] - 2) {
                        $wk_inputflg = 9;
                    }
                }
                # 夜
                if ($data_vildata[3] == 2){
                    if ($wk_logdata[0] == $data_vildata[2]){
                        if ($wk_logdata[1] == 2 || $wk_logdata[1] == 50) {
                            $wk_msgwriteflg = 1;
                        }
                        if ($wk_logdata[1] == 3) {
                            if($sys_plyerno == 60){ #観戦
                                $wk_msgwriteflg = 2;
                            }else{
                                if($data_player[$sys_plyerno][3] ne 'WLF' && $data_player[$sys_plyerno][1] eq 'A') {
                                    $wk_msgwriteflg = 2;
                                }else{
                                    $wk_msgwriteflg = 3;
                            	}
                            }
                        }
                    }
                    if ($wk_logdata[0] <= $data_vildata[2] - 1) {
                        $wk_inputflg = 9;
                    }
                }
            }
            # ログ
            if ($data_vildata[0] == 2 && $sys_logviewflg == 1 && $sys_storytype == "1"){
                if ($wk_logdata[0] != 99){
                   	if ($wk_logdata[1] <= 50 && $wk_logdata[1] != 3){
                        $wk_msgwriteflg = 1;
                    }
                    if ($wk_logdata[1] == 3) {
                        $wk_msgwriteflg = 3;
                    }
                }
            }
            if ($wk_msgwriteflg == 1){
                print "<TR>";
                if ($wk_logdata[2] == 0) {
                    print "<TD colspan=\"2\">$wk_logdata[3]</TD>";
                }
                if ($wk_logdata[2] >= 1 && $wk_logdata[2] <= 22) {
                    print "<TD valign=\"top\" width=\"140\"><FONT color=\"$wk_color[$data_player[$wk_logdata[2]][6]]\">◆</FONT><b>$data_player[$wk_logdata[2]][8]</b>さん</TD><TD>「".$wk_logdata[3]."」</TD>";
                }
                if ($wk_logdata[2] == 23) {
                    print "<TD valign=\"top\"><FONT color=\"FF9900\">◆<b>ゲームマスター</b></FONT></TD><TD>「".$wk_logdata[3]."」</TD>";
                }
                if ($wk_logdata[2] == 24) {
                    print "<TD valign=\"top\">◆<b>村人達</b></TD><TD>".$wk_logdata[3]."</TD>";
                }
                if ($wk_logdata[2] >= 31 && $wk_logdata[2] <= 50) {
                    print "<TD colspan=\"2\"><IMG src=\"".$imgpath;
                    if ($wk_logdata[2] == 31) {
                        print "msg.gif";
                    }
                    if ($wk_logdata[2] == 32) {
                        print "ampm.gif";
                    }
                    if ($wk_logdata[2] == 33) {
                        print "dead1.gif";
                    }
                    if ($wk_logdata[2] == 34) {
                        print "dead2.gif";
                    }
                    if ($wk_logdata[2] == 35) {
                        print "dead3.gif";
                    }
                    if ($wk_logdata[2] == 41) {
                        print "hum.gif";
                    }
                    if ($wk_logdata[2] == 42) {
                        print "wlf.gif";
                    }
                    if ($wk_logdata[2] == 43) {
                        print "ura.gif";
                    }
                    if ($wk_logdata[2] == 44) {
                        print "bgd.gif";
                    }
                    print "\" width=\"32\" height=\"32\" border=\"0\"> $wk_logdata[3]</TD>";
                }
            	print "</TR>";
            }
            if ($wk_msgwriteflg == 2){
                print "<TR><TD valign=\"top\">◆狼の遠吠え<FONT color=\"#FF0000\"></TD><TD>「アオォーーン・・・」</FONT></TD></TR>";
            }
            if ($wk_msgwriteflg == 3){
                print "<TR><TD valign=\"top\" width=\"140\">◆<b>$data_player[$wk_logdata[2]][8]</b>さんの遠吠え</TD><TD><FONT color=\"#FF0000\">「".$wk_logdata[3]."」</FONT></TD></TR>";
            }
        }else{
            $wk_inputflg = 9;
        }
    }
    close(IN);
    print "</TBODY></TABLE>\n";
}
#---------------------------------------------------------------------
sub disp_command{
    if($sys_plyerno == 60){
        return();
    }
    print "<TR><TD class=\"CLSTD01\">◆ 行動設定</TD></TR>\n";
    print "<TR><TD>\n";
    print "<TABLE cellpadding=\"0\" cellspacing=\"0\"><TBODY>";
    print "<TR><TD>行動内容：</TD>";
    print "<TD><SELECT name=\"COMMAND\">";
    if ($sys_plyerno <= 22) {
    	if ($data_player[$sys_plyerno][1] eq 'A' || $data_vildata[0]==2) {
            if ($data_vildata[3]==1 || $data_vildata[0]==2){
                print "<OPTION value=\"MSG\">発　言 [発言内容]</OPTION>\n";
                print "<OPTION value=\"MSG2\">強く発言 [発言内容]</OPTION>\n";
                print "<OPTION value=\"MSG3\">弱く発言 [発言内容]</OPTION>\n";
            }
            if ($data_vildata[0]==0) {
                print "<OPTION value=\"NAMECHG\">名前変更(10字以内) [発言内容]</OPTION>\n";
                print "<OPTION value=\"PROFILE\">プロフィール修正(40字以内) [発言内容]</OPTION>\n";
                if ($sys_plyerno == 1) {
                    print "<OPTION value=\"VILNAME\">村名変更(8字以内) [発言内容]</OPTION>\n";
                }
            }
            if ($data_vildata[0]==1) {
                if ($data_vildata[3]==2) {
                    if ($data_player[$sys_plyerno][3] eq 'WLF'){
                        print "<OPTION value=\"MSGWLF\">遠吠え [発言内容]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'WLF' && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"KILL\">殺　る [行動対象]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'URA' && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"FORTUNE\">占　う [行動対象]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'BGD' && $data_vildata[2] >= 2 && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"GUARD\">護　衛 [行動対象]</OPTION>\n";
                    }
                }
                if ($data_vildata[3]==1 && $data_player[$sys_plyerno][2] == 0){
                    print "<OPTION value=\"VOTE\">投　票 [行動対象]</OPTION>\n";
                }
                if ($data_vildata[3]==1 && $data_player[$sys_plyerno][11] == 0){
                    print "<OPTION value=\"SILENT\">沈　黙</OPTION>\n";
                }
            }
        }else{
    		print "<OPTION value=\"MSG0\">霊　話 [発言内容]</OPTION>\n";
    	}
	}
    # 管理者
    if ($sys_plyerno == 50) {
	    print "<OPTION value=\"MSGM\">管理者メッセージ [発言内容]</OPTION>\n";
	    print "<OPTION value=\"MSGM0\">管理者霊　話 [発言内容]</OPTION>\n";
	    print "<OPTION value=\"VOTECHK\">投票集計</OPTION>\n";
	    print "<OPTION value=\"SHOCK\">突然死 [行動対象]</OPTION>\n";
        if ($data_vildata[0]==0){
            print "<OPTION value=\"START\">ゲームの開始(妖狐無し)</OPTION>\n";
            print "<OPTION value=\"STARTF\">ゲームの開始(妖狐有り)</OPTION>\n";
        }
	}
	print "<OPTION value=\"\">更　新</OPTION>\n";
    print "</SELECT></TD>";
    print "<TD width=\"6\"></TD>";
	print "<TD>行動対象：</TD>";
	print "<TD><SELECT name=\"CMBPLAYER\">";
	for ($i = 1; $i <= $data_vildata[1]; $i++) {
        if ($i != $sys_plyerno && $data_player[$i][1] eq 'A') {
            print "<OPTION value=\"$data_player[$i][0]\">$data_player[$i][8]</OPTION>\n";
        }
	}
    print "</SELECT></TD></TR>";
    print "</TBODY></TABLE>";
    #print "発言内容：<INPUT type=\"text\" size=\"100\" name=\"TXTMSG\"><BR>\n";
    print "<TABLE cellpadding=\"0\" cellspacing=\"0\"><TBODY><TR>";
    print "<TD valign=\"top\">発言内容：</TD><TD><TEXTAREA rows=\"3\" cols=\"70\" name=\"TXTMSG\"></TEXTAREA></TD>\n";
    print "</TR></TBODY></TABLE>";
    print "<INPUT type=\"submit\" value=\"上の内容で行動\">\n";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_msgdead{
    $wk_writeflg = 0;
    if ($data_vildata[0] == 1 && ($data_player[$sys_plyerno][1] eq 'D' || $sys_plyerno == 50)) {
        $wk_writeflg = 1;
    }
    if ($data_vildata[0] == 2 && $sys_logviewflg == 0){
        $wk_writeflg = 1;
    }
    if ($data_vildata[0] == 2 && $sys_logviewflg == 1 && $sys_storytype == "2"){
        $wk_writeflg = 2;
    }

    if ($wk_writeflg >= 1){
        print "<TR><TD class=\"CLSTD01\">◆ 幽霊の間</TD></TR>\n";
        print "<TR><TD class=\"CLSTD02\">\n";
        print "<TABLE cellpadding=\"0\" class=\"CLSTABLE2\"><TBODY>";
        open(IN, $file_log);
        $wk_msgcount = 0;
        $wk_inputflg = 0;
        while ($wk_inputflg == 0) {
            if ($_ = <IN>) {
                @wk_logdata = split(/,/, $_);
                if ($wk_logdata[0] == 99){
                    $wk_msgcount++;
                    print "<TR>\n";
                    if ($wk_logdata[2] == 23) {
                        print "<TD valign=\"top\"><FONT color=\"FF6600\">◆<b>ゲームマスター</b></FONT></TD><TD>「".$wk_logdata[3]."」</TD>";
                    }else{
                    	print "<TR><TD valign=\"top\" width=\"140\"><FONT color=\"$wk_color[$data_player[$wk_logdata[2]][6]]\">◆</FONT><b>$data_player[$wk_logdata[2]][10]</b>さん</TD><TD>「".$wk_logdata[3]."」</TD></TR>";
                	}
                    print "</TR>\n";
                }
                if ($wk_msgcount >= 20 && $wk_writeflg == 1){
                    $wk_inputflg = 9;
                }
            }else{
                $wk_inputflg = 9;
            }
        }
        close(IN);
        print "</TBODY></TABLE>\n";
        print "</TD></TR>\n";
    }
}
#---------------------------------------------------------------------
sub disp_foot{
    print "</TBODY></TABLE></FORM></BODY>\n";
    print "</HTML>\n";
}
#---------------------------------------------------------------------
sub sub_judge{
    $wk_alivewlf = 0;
    $wk_alivehum = 0;
    $wk_alivefox = 0;
    for ($i = 1; $i <= $data_vildata[1]; $i++) {
        if ($data_player[$i][1] eq 'A'){
            if ($data_player[$i][3] eq 'WLF'){
                $wk_alivewlf++;
            }elsif ($data_player[$i][3] eq 'FOX'){
                $wk_alivefox++;
            }else{
                $wk_alivehum++;
            }
        }
    }
    if ($wk_alivewlf == 0) {
        if ($wk_alivefox == 0) {
            $data_vildata[0] = 2;
            $data_vildata[2]++;
            $data_vildata[3] = 1;
            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                if ($data_player[$i][3] eq 'WLF' || $data_player[$i][3] eq 'MAD' || $data_player[$i][3] eq 'FOX'){
                    $data_player[$i][5] = 'L';
                }else{
                    $data_player[$i][5] = 'W';
                }
            }
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">人狼の血を根絶することに成功しました！</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">「$chr_hum」の勝利です！</FONT>");
        }else{
            $data_vildata[0] = 2;
            $data_vildata[2]++;
            $data_vildata[3] = 1;
            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                if ($data_player[$i][3] eq 'FOX'){
                    $data_player[$i][5] = 'W';
                }else{
                    $data_player[$i][5] = 'L';
                }
            }
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">人狼がいなくなった今、我の敵などもういない。</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">「$chr_fox」の勝利です！</FONT>");
        }
    }
    if ($wk_alivewlf >= $wk_alivehum) {
        if ($wk_alivefox == 0) {
            $data_vildata[0] = 2;
            $data_vildata[2]++;
            $data_vildata[3] = 1;
            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                if ($data_player[$i][3] eq 'WLF' || $data_player[$i][3] eq 'MAD'){
                    $data_player[$i][5] = 'W';
                }else{
                    $data_player[$i][5] = 'L';
                }
            }
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">最後の一人を食い殺すと人狼達は次の獲物を求めて村を後にした・・・。</FONT>");
            &msg_write($data_vildata[2], 1, 42,"<FONT size=\"+2\" color=\"#DD0000\">「$chr_wlf」の勝利です！</FONT>");
        }else{
            $data_vildata[0] = 2;
            $data_vildata[2]++;
            $data_vildata[3] = 1;
            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                if ($data_player[$i][3] eq 'FOX'){
                    $data_player[$i][5] = 'W';
                }else{
                    $data_player[$i][5] = 'L';
                }
            }
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">マヌケな人狼どもを騙すことなど容易いことだ。</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">「$chr_fox」の勝利です！</FONT>");
        }
    }
}
#---------------------------------------------------------------------
# Cookieの値を読み出す
#
sub getCookie {
    local($xx, $name, $value);
    foreach $xx (split(/; */, $ENV{'HTTP_COOKIE'})) {
        ($name, $value) = split(/=/, $xx);
        $value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C", hex($1))/eg;
        $COOKIE{$name} = $value;
    }
}

#---------------------------------------------------------------------
# Cookieに値を書き込むためのSet-Cookie:ヘッダを生成する
#
sub setCookie {
    local($tmp, $val);
    $val = $_[1];
    $val =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
    $tmp = "Set-Cookie: ";
    $tmp .= "$_[0]=$val; ";
    $tmp .= "expires=Thu, 1-Jan-2030 00:00:00 GMT;\n";
    return($tmp);
}
