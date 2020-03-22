data_dir=$PI_HOME/.data/gcp-text-to-speech
config_dir=$PI_HOME/.config/gcp-text-to-speech
case $1 in
	setup)
		echo Making aehe-speak ready...
		mkdir -p $data_dir
		touch $data_dir/keys.csv
		chmod 775 $data_dir/keys.csv
		mkdir -p $config_dir
		touch $config_dir gcp_credentials.json
		echo Installing jq...
		sudo apt-get install jq
		echo Installing mpg123...
		sudo apt-get install mpg123
		echo "Set google application credentials, for more details: https://cloud.google.com/text-to-speech/docs/quickstart-protocol"
		read -p "Press enter to continue"
		nano $config_dir/gcp_credentials.json
		echo Install GCP Cloud SDK, if not installed see: https://cloud.google.com/sdk/docs#deb
		;;
	add)
		export GOOGLE_APPLICATION_CREDENTIALS=$config_dir/gcp_credentials.json
		payload="{\"input\":{\"text\":\"$3\"},\"voice\":{\"languageCode\":\"en-gb\",\"name\":\"en-GB-Wavenet-C\",\"ssmlGender\":\"FEMALE\"},\"audioConfig\":{\"audioEncoding\":\"MP3\"}}"
		curl -X POST \
			-H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
			-H "Content-Type: application/json; charset=utf-8" \
			-d "$payload" \
			https://texttospeech.googleapis.com/v1/text:synthesize > $data_dir/$2.json
		jq -r ".audioContent" $data_dir/$2.json > $data_dir/$2.b64
		base64 -d $data_dir/$2.b64 > $data_dir/$2.mp3
		rm $data_dir/$2.json
		rm $data_dir/$2.b64
		echo "\"$2\",\"$3\"" >> $data_dir/keys.csv
		chmod 755 $data_dir/$2.mp3
		echo New key created: $2
		;;
	say)
		# sudo omxplayer --no-osd -o alsa $data_dir/$2.mp3
		mpg123 -q $data_dir/$2.mp3
		;;
	*)
		echo "Invalid argument: $1"
		echo "Available arguments are:"
		echo "========================"
		echo "setup             : Initialize speak"
		echo "add <key> <text>  : Creates new speech file with provided key and text"
	       	echo "say <key>         : Speaks the text for provided key added in 'add' command"
		echo "------------------------"
		echo "example           : speak.sh add GREET \"Hello! How are you?\""
		;;
esac
