#!/usr/local/bin/perl

#===========================================================
# jinro: Version 2004.02.02a
#===========================================================

require './jcode.pl';

#-[ �ݒ�J�n ]-----------------------------------------------------------

# �Q�[����
$sys_title = "�u���͐l�T�Ȃ��H�v�X�N���v�g";
# �摜�t�H���_
$imgpath = "http://www.xxx.co.jp/~yyy/img/";
#CGI �p�X�t�@�C����
$cgi_path = "http://www.xxx.co.jp/~yyy/cgi-bin/cgi_jinro.cgi";
# �v���C���[�f�[�^ �p�X�t�@�C���� (�g���q����)
$dat_path = "./dat_jinro";
# ���O�f�[�^ �p�X�t�@�C���� (�g���q����)
$log_path = "./dat_jinrolog";
# �߂�p�X
$return_url = "http://www.xxx.co.jp/~yyy/jinro_index.htm";
# ���b�N�t�@�C�� �p�X
$lock_path = "./lock/jinro.loc";
# PASSWORD
$sys_pass = 'pass';

#�L�����N�^�[
$chr_hum = '���@�l';
$chr_wlf = '�l�@�T';
$chr_ura = '�肢�t';
$chr_nec = '��\\��';
$chr_mad = '���@�l';
$chr_fre = '���L��';
$chr_bgd = '��@�l';
$chr_fox = '�d�@��';

#-[ �ݒ�I�� ]-----------------------------------------------------------

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
	$code = ord(substr("��", 0, 1));
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
                print "<H1>�t�@�C�����b�N</H1>\n";
                print "�ēx�A�N�Z�X���肢���܂��B<BR>\n";
                print "<A href='javascript:window.history.back()'>�߂�</A>\n";
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

# ***************************************************************** ���O�C���L��
if ($FORM{'TXTLOGIN'} ne '') {
    # =================================================================== �����O�C�� 
    if ($sys_loginflg eq '1') {
        #--------------------------------------------------------------------- �G���g���[���� 
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
                    &msg_write(0, 1, 31,"�u<b>$FORM{'TXTNAME'}</b>����v�����ւ���Ă��܂����B");
                    $wk_entryflg = 1;
                }
            }
            # Print HTML document
            &disp_head1;
            print "<TR><TD>\n";
            if($wk_entryflg == 1){
                print "�A�i�^��$data_no�l�ڂ̑����Ƃ��ēo�^���������܂����B\n";
            }elsif($wk_entryflg == 2){
                print "�\\���󂠂�܂���B���ɃQ�[�����J�n���Ă��܂��B\n";
            }elsif($wk_entryflg == 3){
                print "�\\���󂠂�܂���B���ɂQ�Q���o�^����Ă��܂��B\n";
            }else{
                print "���͍��ڂ�����������܂���B\n";
            }
            print "</TD></TR>\n";
        }
        #--------------------------------------------------------------------- ���O�C������
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
                print "�p�X���[�h������������܂���B\n";
            }
        }
        #--------------------------------------------------------------------- ���O�{��
        if ($FORM{'COMMAND'} eq 'LOGVIEW') {
            $sys_loginflg = '2';
            $sys_plyerno = 60;
            $sys_logviewflg = 1;
        }
    }
    #=================================================================== ���O�C���n�j
    if ($sys_loginflg eq '2') {

        # ���݂̏�Ԃ��m�F
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

        #2�d���e�h�~
        if ($data_vildata[6] == $FORM{'FORMID'}) {
            $FORM{'COMMAND'} = '';
        }
        $data_vildata[6] = $FORM{'FORMID'};
        
        #=================================================================== �J�n�O
        if($data_vildata[0]==0){
            #--------------------------------------------------------------------- �J�n
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
                &msg_write(1, 50, 32,"<FONT size=\"+1\">�P���ڂ̖�ƂȂ�܂����B</FONT>");
            }
            #--------------------------------------------------------------------- ���b�Z�[�W
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
            #--------------------------------------------------------------------- ���O�ύX
            if ($FORM{'COMMAND'} eq 'NAMECHG' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 20){
                    $data_player[$sys_plyerno][8] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- �v���t�B�[���ύX
            if ($FORM{'COMMAND'} eq 'PROFILE' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 80){
                    $data_player[$sys_plyerno][9] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- �����ύX
            if ($FORM{'COMMAND'} eq 'VILNAME' && $wk_txtmsg1 ne '') {
                if ($wk_txtmsglen <= 16){
                    $data_vildata[5] = $wk_txtmsg1;
                }
            }
            #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
            if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                # [ msg write ]
                &msg_write(0, 1, 23, $wk_txtmsg2);
            }
        }
        #=================================================================== �n�m�o�k�`�x�I
        if($data_vildata[0]==1){
            #--------------------------------------------------------------------- [ �� ]
            if($data_vildata[3]==1){
                #--------------------------------------------------------------------- ���b�Z�[�W
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
                #--------------------------------------------------------------------- �� �b
                if ($FORM{'COMMAND'} eq 'MSG0' && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, $sys_plyerno, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write($data_vildata[2], 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'MSGM0'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- ����
                if ($FORM{'COMMAND'} eq 'SILENT') {
                    $data_player[$sys_plyerno][11] = 1;
                    # ����
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
                    # ���� ����
                    if(int($wk_cnt_live / 2) < $wk_cnt_silent){
                        $data_vildata[4] += 4;
                        if ($data_vildata[4] >= 48){
                            $data_vildata[4] = 48;
                        }
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            $data_player[$i][11] = 0;
                        }
                        &msg_write($data_vildata[2], 1, 24, '�u�E�E�E�E�E�E�B�v�P���Ԃقǂ̒��ق��������B');
                    }
                }
                #--------------------------------------------------------------------- ���[
                if (($FORM{'COMMAND'} eq 'VOTE' && $data_player[$sys_plyerno][2] == 0 && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') || $FORM{'COMMAND'} eq 'VOTECHK') {
                	if ($FORM{'COMMAND'} eq 'VOTE'){
                	    $data_player[$sys_plyerno][2] = $FORM{'CMBPLAYER'};
                	}
                    # ���[����
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
                                $wk_votetable = $wk_votetable."<TR><TD><b>$data_player[$i][8]</b>����</TD><TD>$wk_votecount[$i] �[</TD><TD>���[�� �� <b>$data_player[$data_player[$i][2]][8]</b>����</TD></TR>";
                                if ($wk_votecount[$wk_topvote] < $wk_votecount[$i]){
                                    $wk_topvote = $i;
                                }
                            }
                        }
                        $wk_votetable = $wk_votetable."</TABLE>";
                        &msg_write($data_vildata[2], 2, 0,"$wk_votetable");
                        &msg_write($data_vildata[2], 2, 0,"<BR><FONT size=\"+1\">$data_vildata[2]���� ���[���ʁB</FONT>");
                        $wk_topvotecheck = 0;
                        for ($i = 1; $i <= $data_vildata[1]; $i++) {
                            if ($wk_votecount[$wk_topvote] == $wk_votecount[$i]){
                                $wk_topvotecheck++;
                            }
                        }
                        if ($wk_topvotecheck == 1){
                            # ���[�I��
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

                            # [ �������� ]
                            &sub_judge;
                            
                            if ($data_vildata[0] == 1) {
                                &msg_write($data_vildata[2], 2, 33,"<b>$data_player[$wk_topvote][8]</b>����͑������c�̌���<FONT color=\"#ff0000\">���Y����܂����E�E�E�B</FONT>");
                                &msg_write($data_vildata[2], 50, 32,"<FONT size=\"+1\">$data_vildata[2]���ڂ̖�ƂȂ�܂����B</FONT>");
                            }
                        }else{
                            for ($i = 1; $i <= $data_vildata[1]; $i++) {
                                $data_player[$i][2] = 0;
                            }
                            &msg_write($data_vildata[2], 2, 31,"<FONT size=\"+1\">�ē��[�ƂȂ�܂����B</FONT>");
                        }
                    }
                }
                #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'SHOCK' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$FORM{'CMBPLAYER'}][1] = 'D';
                    &msg_write($data_vildata[2], 1, 34,"<b>$data_player[$FORM{'CMBPLAYER'}][8]</b>����͓s���ɂ��<FONT color=\"#ff0000\">�ˑR�����܂����E�E�E�B</FONT>");
                }
            }
            #--------------------------------------------------------------------- [ �� ]
            if($data_vildata[3] == 2){
                #-------------------------- ���i��
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
                #-------------------------- �E�Q�\��
                if ($FORM{'COMMAND'} eq 'KILL' && $data_player[$FORM{'CMBPLAYER'}][3] ne 'WLF' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    for ($i = 1; $i <= $data_vildata[1]; $i++) {
                        if ($data_player[$i][3] eq 'WLF') {
                            $data_player[$i][4] = $FORM{'CMBPLAYER'};
                            #&msg_write($data_vildata[2], 11, 42,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>�����_���܂��B</FONT>");
                        }
                    }
                    &msg_write($data_vildata[2], 11, 42,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>�����_���܂��B");
                }
                #-------------------------- �肢�t
                if ($FORM{'COMMAND'} eq 'FORTUNE' && $data_player[$sys_plyerno][4] == 0 && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$sys_plyerno][4] = $FORM{'CMBPLAYER'};
                    &msg_write($data_vildata[2], 12, 43,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>�����肢�܂��B");
                }
                #-------------------------- ��l
                if ($FORM{'COMMAND'} eq 'GUARD' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$sys_plyerno][4] = $FORM{'CMBPLAYER'};
                    &msg_write($data_vildata[2], 13, 44,"<b>".$data_player[$FORM{'CMBPLAYER'}][8]."</b>�������q���܂��B");
                }
                
                #--------------------------- �� �b
                if ($FORM{'COMMAND'} eq 'MSG0' && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, $sys_plyerno, $wk_txtmsg2);
                }
                #--------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'MSGM'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write($data_vildata[2], 2, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'MSGM0'  && $wk_txtmsg1 ne '') {
                    # [ msg write ]
                    &msg_write(99, 1, 23, $wk_txtmsg2);
                }
                #--------------------------------------------------------------------- ��I������
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
                        
                        # ��q�A�d�ϔ���
                        if ($wk_targetwlf != $wk_targetbgd && $data_player[$wk_targetwlf][3] ne 'FOX') {
                            $data_player[$wk_targetwlf][1] = 'D';
                            &msg_write($data_vildata[2], 4, 34,"<b>$data_player[$wk_targetwlf][8]</b>����͗���<FONT color=\"#ff0000\">���c�Ȏp�Ŕ������ꂽ�E�E�E�B</FONT>");
                        }
                        if ($data_player[$wk_targetura][3] eq 'FOX') {
                            $data_player[$wk_targetura][1] = 'D';
                            &msg_write($data_vildata[2], 4, 34,"<b>$data_player[$wk_targetura][8]</b>����͗���<FONT color=\"#ff0000\">���c�Ȏp�Ŕ������ꂽ�E�E�E�B</FONT>");
                        }

                        # [ �������� ]
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
                            &msg_write($data_vildata[2], 50, 32,"<FONT size=\"+1\">$data_vildata[2]���ڂ̒��ƂȂ�܂����B</FONT>");
                        }
                    }
                }
                #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
                if ($FORM{'COMMAND'} eq 'SHOCK' && $data_player[$FORM{'CMBPLAYER'}][1] eq 'A') {
                    $data_player[$FORM{'CMBPLAYER'}][1] = 'D';
                    &msg_write($data_vildata[2], 2, 34,"<b>$data_player[$FORM{'CMBPLAYER'}][8]</b>����͓s���ɂ��<FONT color=\"#ff0000\">�ˑR�����܂����E�E�E�B</FONT>");
                }
            }
        }
        #=================================================================== �Q�[���I��
        if($data_vildata[0]==2){
            #--------------------------------------------------------------------- ���b�Z�[�W
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
            #--------------------------------------------------------------------- �Ǘ��҃��b�Z�[�W
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
            print "<TR><TD class=\"CLSTD01\">�� �o����</TD></TR>\n";
            print "<TR><TD>\n";
            # [ ���t ]
            &disp_time(@data_vildata);
            print "<BR>\n";
            # [ �R�����g ]
            &disp_msg;
            print "</TD></TR>\n";
        }
        
        # [ �s���ݒ� ]
        &disp_command;

        # [ �R�����gdead ]
        &disp_msgdead;

        
        #�f�[�^��������
        if($sys_plyerno <= 50){
            &data_write;
        }
    }
    
    print "</TD></TR>\n";
    print "<TR><TD class=\"CLSTD01\"><A href=\"$return_url\">�߂�</A>\n";
    print "<INPUT type=\"hidden\" name=\"TXTPNO\" value=\"$sys_plyerno\">";
    print "<INPUT type=\"hidden\" name=\"VILLAGENO\" value=\"$sys_village\">";
    print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"2\">";
    $wk_rnd = int(rand(1000000)) + 1;
    print "<INPUT type=\"hidden\" name=\"FORMID\" value=\"$wk_rnd\">";
    print "</TD></TR>\n";
}
# ***************************************************************** ���O�C���Ȃ�
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
            @data_vildata = (0,0,0,1,0,'�ǂ�����');
        
            &data_write;
            open(OUT, "> ".$file_log);
            close(OUT);
        
            print "<TR><TD align=\"center\">�V�K�ɍ쐬���܂����B</TD></TR>\n";
        } elsif ($FORM{'COMMAND'} eq 'DELVILLAGE') {
            open(IN, $dat_path.$sys_village.".dat");
            @wk_vildata = split(/,/,<IN>);
            close(IN);
            if ($wk_vildata[0] == 2) {
                $file_pdata = $dat_path.$sys_village.".dat";
                unlink($file_pdata);
                $file_log   = $log_path.$sys_village.".dat";
                unlink($file_log);
                print "<TR><TD align=\"center\">�� $sys_village�Ԃ��폜���܂����B</TD></TR>\n";
            } else {
                print "<TR><TD align=\"center\">�Q�[�����I�����Ă���폜���Ă��������B</TD></TR>\n";
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
            print "<TR><TD align=\"center\">�� $sys_village�ԃQ�[���������I�����܂����B</TD></TR>\n";
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
                print "<TR><TD align=\"center\">���������������ǂ����B</TD></TR>\n";
            }
        }
    }
}

# [ FOOT ]
&disp_foot;

# Lock����
rmdir($lock_path);

##########################################################################################################
# �T�u���[�`��
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
    # Cookie�̒l�𓾂�
    &getCookie();
    $sys_default0 = $COOKIE{'SELECTROOM'};
    if ($sys_default0 eq "") {
        $sys_default0 = 0;
    }
    
    print "<TR><TD>\n";
    print "<TABLE>\n";
    
    print "<TR><TD>����I��</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        @wk_vildata = split(/,/,<IN>);
        print "<OPTION value=\"$wk_fileno\" ";
        if ($sys_default0 == $wk_fileno) {
            print "selected";
        }
        print ">�� �Z��$wk_fileno�� $wk_vildata[5]��</OPTION>\n";
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";

    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"���ɍs��\"></TD></TR>\n";
    print "</TABLE>\n";
    #print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"\">\n";
    print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"ENTER\">\n";
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_login{
    # Cookie�̒l�𓾂�
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
    print "<TR><TD>����I��</TD><TD>�� �Z��$sys_village�� $wk_vildata[5]��</TD></TR>\n";
    print "<TR><TD>���O��I��</TD><TD><SELECT name=\"CMBPLAYER\">\n";
    print "<OPTION value=\"0\">���@�l�i�ϐ�j</OPTION>\n";
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
    print ">�Ǘ���</OPTION>\n";
    print "</SELECT></TD></TR>\n";
    
    print "<TR><TD>�p�X���[�h</TD><TD><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\" value=\"$sys_default2\"></TD></TR>\n";
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"���ɍs��\"></TD></TR>\n";
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

    print "<TR><TD>����I��</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        print "<OPTION value=\"$wk_fileno\">�� �Z�� $wk_fileno��</OPTION>\n";
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";
    
    print "<TR><TD>�V�KNO</TD><TD>��NO $wk_fileno</TD></TR>";
    
    print "<TR><TD>�����I��</TD><TD><SELECT name=\"COMMAND\">\n";
    print "  <OPTION value=\"NEWVILLAGE\">�����쐬</OPTION>\n";
    print "  <OPTION value=\"DELVILLAGE\">���̍폜</OPTION>\n";
    print "  <OPTION value=\"ENDVILLAGE\">�Q�[���̋����I��</OPTION>\n";
    print "</SELECT></TD></TR>\n";

    print "<TR><TD>�p�X���[�h</TD><TD><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\"></TD></TR>\n";
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"�������s\"></TD></TR>\n";
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
    
        print "<TR><TD align=\"center\"><B><FONT size=\"+2\">�����o�^��</FONT></B></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";
    
        print "<TR><TD align=\"center\">������I�����Ă��������B</TD></TR>\n";
        print "<TR><TD align=\"center\"><SELECT name=\"VILLAGENO\">\n";
        $wk_fileno = 1;
        while (open(IN, $dat_path.$wk_fileno.".dat")) {
            @wk_vildata = split(/,/,<IN>);
            if ($wk_vildata[0] == 0) {
                print "<OPTION value=\"$wk_fileno\">�� �Z��$wk_fileno�� $wk_vildata[5]��</OPTION>\n";
            }
            $wk_fileno++;
            close(IN);
        }
        print "  </SELECT></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";
    
        print "<TR><TD align=\"center\">���A�i�^��HN����͂��Ă��������B�i10�����j</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"20\" maxlength=\"10\" type=\"text\" name=\"TXTHN\"></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";
    
        print "<TR><TD align=\"center\">���A�i�^�̕\\���F��I�����Ă��������B</TD></TR>\n";
        print "<TR><TD align=\"center\"><SELECT name=\"CMBCOLOR\">\n";
        print "<OPTION value=\"1\" selected>���D lightglay</OPTION>\n";
        print "<OPTION value=\"2\">�ÊD darkglay</OPTION>\n";
        print "<OPTION value=\"3\">�� yellow</OPTION>\n";
        print "<OPTION value=\"4\">�� orange</OPTION>\n";
        print "<OPTION value=\"5\">�� red</OPTION>\n";
        print "<OPTION value=\"6\">�� lightblue</OPTION>\n";
        print "<OPTION value=\"7\">�� blue</OPTION>\n";
        print "<OPTION value=\"8\">�� green</OPTION>\n";
        print "<OPTION value=\"9\">�� purple</OPTION>\n";
        print "<OPTION value=\"10\">�� pink</OPTION>\n";
        print "</SELECT></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";

        print "<TR><TD align=\"center\">���A�i�^�̑��l�Ƃ��Ă̖��O����͂��Ă��������B�i10�����j<BR>�i��F�R�c�@�l�Y�j<BR><FONT size=\"-1\">�v���C���͂��̖��O���g�p���܂��BHN���΂�Ȃ����̂��D�܂����ł��B</FONT></TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"20\" maxlength=\"10\" type=\"text\" name=\"TXTNAME\"></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";

        print "<TR><TD align=\"center\">���A�i�^�̑��l�v���t�B�[���������Ă��������B�i40�����j<BR>�i��F�S�O�΁E���c�ƁE���̎w���o�`�����v�E���݂Q�A�e�j</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"60\" maxlength=\"40\" type=\"text\" name=\"TXTPROFILE\"></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";

        print "<TR><TD align=\"center\">���A�i�^�̃��O�C���p�X���[�h����͂��Ă��������B�i���p�p����4�����j<BR>�i���̃v���C���[�ɉ���Ȃ��悤�Ȃ��̂ɂ��Ă��������B�j</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"5\" type=\"password\" maxlength=\"4\" name=\"TXTPASS\"></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";

        print "<TR><TD align=\"center\">�����[���A�h���X����͂��Ă��������B<BR>�i�A���p�Ɏg�p���܂��B�j</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT size=\"40\" type=\"text\" name=\"TXTMAIL\"></TD></TR>\n";
        print "<TR><TD align=\"center\">��</TD></TR>\n";

        print "<TR><TD align=\"center\">�u�������v<BR>���͑��̂��߉Ƒ��̂��߂ɂ����Ď������g�̂��߂�<BR>������������A���܂��܁A����A�Ȃ�ƂȂ��A����邩������Ȃ�<BR>�u�l�T�v�Ɛ킢�������Ƃ𐾂��܂��B</TD></TR>\n";
        print "<TR><TD align=\"center\"><INPUT type=\"submit\" value=\"���ӂ���i�o�^�j\"></TD></TR>\n";
    
        print "</TBODY></TABLE>\n";
        print "</TD></TR></TBODY></TABLE></CENTER>\n";
        print "<INPUT type=\"hidden\" name=\"TXTLOGIN\" value=\"1\">";
        print "<INPUT type=\"hidden\" name=\"COMMAND\" value=\"ENTRY\">\n";
    } else {
        print "�؍݉\\�ȑ�������܂���ł����B";
    }
    print "</TD></TR>\n";
}
#---------------------------------------------------------------------
sub disp_logview{
    # Cookie�̒l�𓾂�
    &getCookie();
    $sys_default0 = $COOKIE{'SELECTROOM'};
    if ($sys_default0 eq "") {
        $sys_default0 = 0;
    }
    
    print "<TR><TD>\n";
    print "<TABLE>\n";
    
    print "<TR><TD>����I��</TD><TD><SELECT name=\"VILLAGENO\">\n";
    $wk_fileno = 1;
    while (open(IN, $dat_path.$wk_fileno.".dat")) {
        @wk_vildata = split(/,/,<IN>);
        if ($wk_vildata[0] == 2) {
            print "<OPTION value=\"$wk_fileno\" ";
            if ($sys_default0 == $wk_fileno) {
                print "selected";
            }
            print ">�� �Z��$wk_fileno�� $wk_vildata[5]��</OPTION>\n";
        }
        $wk_fileno++;
        close(IN);
    }
    print "  </SELECT></TD></TR>\n";

    print "<TR><TD>�b��I��</TD><TD><SELECT name=\"STORYTYPE\">\n";
    print "<OPTION value=\"1\" selected>���l�̐킢</OPTION>\n";
    print "<OPTION value=\"2\">��̒k�b</OPTION>\n";
    print "</SELECT></TD></TR>\n";
    
    print "<TR><TD colspan=\"2\"><INPUT type=\"submit\" value=\"�L�^������\"></TD></TR>\n";
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
    print "<TR><TD class=\"CLSTD01\">�� ���l����</TD></TR>\n";
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
                print "<b>$data_player[$i][10]</b>����<BR>";
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
                    print "<A href=\"mailto:$data_player[$i][12]\?Subject=���m�点\">��</A>";
                    if ($data_player[$i][2] != 0) {
                        print "<FONT color=\"0000FF\">��</FONT>";
                    }
                    if ($data_player[$i][4] != 0) {
                        print "<FONT color=\"00FF00\">��</FONT>";
                    }
                    print "<BR>$data_player[$i][13]";
                }
                print "<BR>";
            }
            if ($data_player[$i][1] eq 'A'){
                print "�i�������j</TD>\n";
            }
            if ($data_player[$i][1] eq 'D'){
                print "�i���@�S�j</TD>\n";
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
        print "<TR><TD class=\"CLSTD01\">�� �A�i�^�̏��</TD></TR>\n";
        if ($data_player[$sys_plyerno][1] eq 'A') {
            print "<TR><TD><TABLE cellspacing=\"0\"><TBODY>\n";
            if ($data_player[$sys_plyerno][3] eq 'HUM') {
                print "<TR><TD><IMG src=\"".$imgpath."hum.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_hum�v�ł��B<BR>";
                print "�y�\\�́z����܂���B�������A�A�i�^�̒m�b�ƗE�C�ő����~�����Ƃ��ł���͂��ł��B</TD></TR>";
            }
            if ($data_player[$sys_plyerno][3] eq 'WLF') {
                print "<TR><TD><IMG src=\"".$imgpath."wlf.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_wlf�v�ł��B<BR>";
                print "�y�\\�́z��̊Ԃɑ��̐l�T�Ƌ��͂����l�ЂƂ�E�Q�ł��܂��B�A�i�^�͂��̋��͂ȗ͂ő��l��H���E���̂ł��B</TD></TR>";
                for ($i = 1; $i <= $data_vildata[1]; $i++) {
        	        if ($data_player[$i][3] eq 'WLF' && $i != $sys_plyerno) {
        	            print "<TR><TD colspan=\"2\">�y�\\�͔����z�ւ荂���l�T�̌����������Ԃ�<b>$data_player[$i][8]</b>����ł��B</TD></TR>";
        	        }
            	}
            	if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">�y�\\�͔����z�A�i�^��<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>������E��\\��ł��B</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'URA') {
                print "<TR><TD><IMG src=\"".$imgpath."ura.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_ura�v�ł��B<BR>";
                print "�y�\\�́z��̊Ԃɑ��l�ЂƂ���u�l�v���u�T�v�����ׂ邱�Ƃ��ł��܂��B�A�i�^�����l�̏����������Ă��܂��B</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">�y�\\�͔����z�肢�̌��ʁA<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>�����";
                    if ($data_player[$data_player[$sys_plyerno][4]][3] eq 'WLF') {
                        print "�u$chr_wlf�v�ł����B"
                    }else{
                        print "�u$chr_hum�v�ł����B"
                    }
                    print "</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'NEC') {
                print "<TR><TD><IMG src=\"".$imgpath."nec.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_nec�v�ł��B<BR>";
                print "�y�\\�́z[�Q���ڈȍ~]���̓��̃����`���҂��u�l�v���u�T�v�����ׂ邱�Ƃ��ł��܂��B�n���ł����A�i�^�̓w�͎���ő傫���v�����邱�Ƃ��s�\\�ł͂���܂���B</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">�y�\\�͔����z�O�����Y���ꂽ<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>�����";
                    if ($data_player[$data_player[$sys_plyerno][4]][3] eq 'WLF') {
                        print "�u$chr_wlf�v�ł����B"
                    }else{
                        print "�u$chr_hum�v�ł����B"
                    }
                    print "</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'MAD') {
                print "<TR><TD><IMG src=\"".$imgpath."mad.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_mad�v�ł��B<BR>";
                print "�y�\\�́z�l�T�̏������A�i�^�̏����ƂȂ�܂��B�A�i�^�͂ł��邩���苶���ď�����������̂ł��B�o�J�ɂȂ�B</TD></TR>";
            }
            if ($data_player[$sys_plyerno][3] eq 'BGD') {
                print "<TR><TD><IMG src=\"".$imgpath."bgd.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_bgd�v�ł��B<BR>";
                print "�y�\\�́z[�Q���ڈȍ~]��̊Ԃɑ��l�ЂƂ���w�肵�l�T�̎E�Q�����邱�Ƃ��ł��܂��B�l�T�̃R�R����ǂނ̂ł��B</TD></TR>";
                if ($data_player[$sys_plyerno][4] > 0) {
                    print "<TR><TD colspan=\"2\">�y�\\�͔����z�A�i�^��<B>$data_player[$data_player[$sys_plyerno][4]][8]</B>�������q���Ă��܂��B</TD></TR>";
                }
            }
            if ($data_player[$sys_plyerno][3] eq 'FRE') {
                print "<TR><TD><IMG src=\"".$imgpath."fre.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_fre�v�ł��B<BR>";
                print "�y�\\�́z�A�i�^�͂����ЂƂ��$chr_fre������ł��邩��m�邱�Ƃ��ł��܂��B�������Ԃ����ɔ�׉i���\\�͂ł��B�A�i�^�ɂ͐������鎞�Ԃ��^����ꂽ�̂ł��B�Y�݂Ȃ����B</TD></TR>";
            	for ($i = 1; $i <= $data_vildata[1]; $i++) {
        	        if ($data_player[$i][3] eq 'FRE' && $i != $sys_plyerno) {
        	            print "<TR><TD colspan=\"2\">�y�\\�͔����z�����ЂƂ��$chr_fre��<b>$data_player[$i][8]</b>����ł��B</TD></TR>";
        	        }
            	}
            }
            if ($data_player[$sys_plyerno][3] eq 'FOX') {
                print "<TR><TD><IMG src=\"".$imgpath."fox.gif\" width=\"32\" height=\"32\" border=\"0\"></TD>";
                print "<TD>�A�i�^�̖����́u$chr_fox�v�ł��B<BR>";
                print "�y�\\�́z�A�i�^�͐l�T�ɎE����邱�Ƃ͂���܂���B����������Ă��܂��Ǝ���ł��܂��܂��B���l���x���A�l�T���x���A����d�ς̂��̂ɂ���̂ł��B</TD></TR>";
            }

            if ($data_player[$sys_plyerno][11] == 1) {
                print "<TR><TD colspan=\"2\">�y���@�فz�A�i�^�͑��̗l�q���f���Ȃ��璾�ق��Ă��܂��B�i�����͂ł��܂��j</TD></TR>";
            }
            if ($data_player[$sys_plyerno][2] != 0) {
                print "<TR><TD colspan=\"2\">�y���@�[�z�A�i�^��<B>$data_player[$data_player[$sys_plyerno][2]][8]</B>����ɓ��[���s���܂����B</TD></TR>";
            }
            print "</TBODY></TABLE></TD></TR>\n";
        }else{
            print "<TR><TD>�A�i�^�͑��₦�܂����E�E�E</TD></TR>\n";
        }
    }
    if($data_vildata[0] == 2 && $sys_plyerno <= 22) {
        print "<TR><TD class=\"CLSTD01\">�� �A�i�^�̏��</TD></TR>\n";
        if ($data_player[$sys_plyerno][5] eq 'W') {
            print "<TR><TD>�A�i�^��<FONT color=\"FF0000\">����</FONT>���܂����B</TD></TR>\n";
        }else{
            print "<TR><TD>�A�i�^��<FONT color=\"0000FF\">�s�k</FONT>���܂����B</TD></TR>\n";
        }
    }
}
#---------------------------------------------------------------------
sub disp_time{
    $wk_faze[0] = '';
    $wk_faze[1] = 'sun.gif';
    $wk_faze[2] = 'moon.gif';
    print "<IMG src=\"".$imgpath."village.gif\" width=\"32\" height=\"32\" border=\"0\"> ";
    print "<FONT size=\"+2\">�` $_[5]�� �`</FONT><BR>";
    print "<IMG src=\"".$imgpath."clock.gif\" width=\"32\" height=\"32\" border=\"0\"> ";
    if($_[2]==0){
        print "<FONT size=\"+2\">�����O��</FONT>";
    }else{
        print "<FONT size=\"+2\">$_[2]</FONT>���� ";
        print "<IMG src=\"".$imgpath.$wk_faze[$_[3]]."\" border=\"0\"> ";
        # ��
        if ($_[3]==1){
            if ($_[4] < 48){
                $wk_hour = int((48 - $_[4]) / 4);
                $wk_min = ((4 - ($_[4] % 4)) % 4) * 15;
                print "���v�܂ł��� <FONT size=\"+2\">$wk_hour</FONT>����";
                if($wk_min > 0){
                    print " <FONT size=\"+2\">$wk_min</FONT>��";
                }
            }else{
                # ���[����
                $wk_nonvotecount = 0;
                for ($i = 1; $i <= $data_vildata[1]; $i++) {
                    if ($data_player[$i][2] == 0 && $data_player[$i][1] eq 'A') {
                        $wk_nonvotecount++;
                    }
                }
                print "���z�����̋�ɒ��݂����Ă��܂��B<FONT size=\"+2\">���[</FONT>���s���Ă��������B<BR>";
                print "����<FONT size=\"+2\">$wk_nonvotecount</FONT>���̓��[�҂��ƂȂ��Ă��܂��B";
            }
        }
        # ��
        if ($_[3]==2){
            if ($_[4] < 48){
                $wk_hour = int((48 - $_[4]) / 4);
                $wk_min = ((4 - ($_[4] % 4)) % 4) * 15;
                print "�閾���܂ł��� <FONT size=\"+2\">$wk_hour</FONT>����";
                if($wk_min > 0){
                    print " <FONT size=\"+2\">$wk_min</FONT>��";
                }
            }else{
                # ���[����
                print "���̋󂪔��݂͂��߂Ă��܂��B<FONT size=\"+2\">�\\�͑Ώ�</FONT>�����肵�Ă��������B<BR>";
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
            # �J�n�O
            if ($data_vildata[0] == 0){
                $wk_msgwriteflg = 1;
            }
            # �Q�[�����A�I���ネ�O�C��
            if ($data_vildata[0] == 1 || ($data_vildata[0] == 2 && $sys_logviewflg == 0)){
                # ��
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
                # ��
                if ($data_vildata[3] == 2){
                    if ($wk_logdata[0] == $data_vildata[2]){
                        if ($wk_logdata[1] == 2 || $wk_logdata[1] == 50) {
                            $wk_msgwriteflg = 1;
                        }
                        if ($wk_logdata[1] == 3) {
                            if($sys_plyerno == 60){ #�ϐ�
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
            # ���O
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
                    print "<TD valign=\"top\" width=\"140\"><FONT color=\"$wk_color[$data_player[$wk_logdata[2]][6]]\">��</FONT><b>$data_player[$wk_logdata[2]][8]</b>����</TD><TD>�u".$wk_logdata[3]."�v</TD>";
                }
                if ($wk_logdata[2] == 23) {
                    print "<TD valign=\"top\"><FONT color=\"FF9900\">��<b>�Q�[���}�X�^�[</b></FONT></TD><TD>�u".$wk_logdata[3]."�v</TD>";
                }
                if ($wk_logdata[2] == 24) {
                    print "<TD valign=\"top\">��<b>���l�B</b></TD><TD>".$wk_logdata[3]."</TD>";
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
                print "<TR><TD valign=\"top\">���T�̉��i��<FONT color=\"#FF0000\"></TD><TD>�u�A�I�H�[�[���E�E�E�v</FONT></TD></TR>";
            }
            if ($wk_msgwriteflg == 3){
                print "<TR><TD valign=\"top\" width=\"140\">��<b>$data_player[$wk_logdata[2]][8]</b>����̉��i��</TD><TD><FONT color=\"#FF0000\">�u".$wk_logdata[3]."�v</FONT></TD></TR>";
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
    print "<TR><TD class=\"CLSTD01\">�� �s���ݒ�</TD></TR>\n";
    print "<TR><TD>\n";
    print "<TABLE cellpadding=\"0\" cellspacing=\"0\"><TBODY>";
    print "<TR><TD>�s�����e�F</TD>";
    print "<TD><SELECT name=\"COMMAND\">";
    if ($sys_plyerno <= 22) {
    	if ($data_player[$sys_plyerno][1] eq 'A' || $data_vildata[0]==2) {
            if ($data_vildata[3]==1 || $data_vildata[0]==2){
                print "<OPTION value=\"MSG\">���@�� [�������e]</OPTION>\n";
                print "<OPTION value=\"MSG2\">�������� [�������e]</OPTION>\n";
                print "<OPTION value=\"MSG3\">�キ���� [�������e]</OPTION>\n";
            }
            if ($data_vildata[0]==0) {
                print "<OPTION value=\"NAMECHG\">���O�ύX(10���ȓ�) [�������e]</OPTION>\n";
                print "<OPTION value=\"PROFILE\">�v���t�B�[���C��(40���ȓ�) [�������e]</OPTION>\n";
                if ($sys_plyerno == 1) {
                    print "<OPTION value=\"VILNAME\">�����ύX(8���ȓ�) [�������e]</OPTION>\n";
                }
            }
            if ($data_vildata[0]==1) {
                if ($data_vildata[3]==2) {
                    if ($data_player[$sys_plyerno][3] eq 'WLF'){
                        print "<OPTION value=\"MSGWLF\">���i�� [�������e]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'WLF' && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"KILL\">�E�@�� [�s���Ώ�]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'URA' && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"FORTUNE\">��@�� [�s���Ώ�]</OPTION>\n";
                    }
                    if ($data_player[$sys_plyerno][3] eq 'BGD' && $data_vildata[2] >= 2 && $data_player[$sys_plyerno][4] == 0){
                        print "<OPTION value=\"GUARD\">��@�q [�s���Ώ�]</OPTION>\n";
                    }
                }
                if ($data_vildata[3]==1 && $data_player[$sys_plyerno][2] == 0){
                    print "<OPTION value=\"VOTE\">���@�[ [�s���Ώ�]</OPTION>\n";
                }
                if ($data_vildata[3]==1 && $data_player[$sys_plyerno][11] == 0){
                    print "<OPTION value=\"SILENT\">���@��</OPTION>\n";
                }
            }
        }else{
    		print "<OPTION value=\"MSG0\">��@�b [�������e]</OPTION>\n";
    	}
	}
    # �Ǘ���
    if ($sys_plyerno == 50) {
	    print "<OPTION value=\"MSGM\">�Ǘ��҃��b�Z�[�W [�������e]</OPTION>\n";
	    print "<OPTION value=\"MSGM0\">�Ǘ��җ�@�b [�������e]</OPTION>\n";
	    print "<OPTION value=\"VOTECHK\">���[�W�v</OPTION>\n";
	    print "<OPTION value=\"SHOCK\">�ˑR�� [�s���Ώ�]</OPTION>\n";
        if ($data_vildata[0]==0){
            print "<OPTION value=\"START\">�Q�[���̊J�n(�d�ϖ���)</OPTION>\n";
            print "<OPTION value=\"STARTF\">�Q�[���̊J�n(�d�ϗL��)</OPTION>\n";
        }
	}
	print "<OPTION value=\"\">�X�@�V</OPTION>\n";
    print "</SELECT></TD>";
    print "<TD width=\"6\"></TD>";
	print "<TD>�s���ΏہF</TD>";
	print "<TD><SELECT name=\"CMBPLAYER\">";
	for ($i = 1; $i <= $data_vildata[1]; $i++) {
        if ($i != $sys_plyerno && $data_player[$i][1] eq 'A') {
            print "<OPTION value=\"$data_player[$i][0]\">$data_player[$i][8]</OPTION>\n";
        }
	}
    print "</SELECT></TD></TR>";
    print "</TBODY></TABLE>";
    #print "�������e�F<INPUT type=\"text\" size=\"100\" name=\"TXTMSG\"><BR>\n";
    print "<TABLE cellpadding=\"0\" cellspacing=\"0\"><TBODY><TR>";
    print "<TD valign=\"top\">�������e�F</TD><TD><TEXTAREA rows=\"3\" cols=\"70\" name=\"TXTMSG\"></TEXTAREA></TD>\n";
    print "</TR></TBODY></TABLE>";
    print "<INPUT type=\"submit\" value=\"��̓��e�ōs��\">\n";
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
        print "<TR><TD class=\"CLSTD01\">�� �H��̊�</TD></TR>\n";
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
                        print "<TD valign=\"top\"><FONT color=\"FF6600\">��<b>�Q�[���}�X�^�[</b></FONT></TD><TD>�u".$wk_logdata[3]."�v</TD>";
                    }else{
                    	print "<TR><TD valign=\"top\" width=\"140\"><FONT color=\"$wk_color[$data_player[$wk_logdata[2]][6]]\">��</FONT><b>$data_player[$wk_logdata[2]][10]</b>����</TD><TD>�u".$wk_logdata[3]."�v</TD></TR>";
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
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">�l�T�̌������₷�邱�Ƃɐ������܂����I</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">�u$chr_hum�v�̏����ł��I</FONT>");
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
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">�l�T�����Ȃ��Ȃ������A��̓G�Ȃǂ������Ȃ��B</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">�u$chr_fox�v�̏����ł��I</FONT>");
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
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">�Ō�̈�l��H���E���Ɛl�T�B�͎��̊l�������߂đ�����ɂ����E�E�E�B</FONT>");
            &msg_write($data_vildata[2], 1, 42,"<FONT size=\"+2\" color=\"#DD0000\">�u$chr_wlf�v�̏����ł��I</FONT>");
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
        
            &msg_write($data_vildata[2], 1, 0,"<FONT size=\"+1\">�}�k�P�Ȑl�T�ǂ����x�����ƂȂǗe�Ղ����Ƃ��B</FONT>");
            &msg_write($data_vildata[2], 1, 41,"<FONT size=\"+2\" color=\"#FF6600\">�u$chr_fox�v�̏����ł��I</FONT>");
        }
    }
}
#---------------------------------------------------------------------
# Cookie�̒l��ǂݏo��
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
# Cookie�ɒl���������ނ��߂�Set-Cookie:�w�b�_�𐶐�����
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
