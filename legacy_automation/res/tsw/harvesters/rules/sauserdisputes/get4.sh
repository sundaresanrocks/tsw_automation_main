day=$(date -d yesterday +%d)
month=$(date -d yesterday +%m)
year=$(date -d yesterday +%Y)
op_dir=/data/harvesters/SAUserDisputes/feed
url=http://tsqasvc01.wsrlab/sa/special.csv?command=dailyreport\&day=${day}\&month=${month}\&year=${year}\&ishtml=0

if [ ! -d "$op_dir" ]; then
  echo "Creating ${op_dir}..."
  mkdir -p ${op_dir}
fi

echo "SAUserDisputes	Fetching user disputes from siteadvisor.com"
echo "SAUserDisputes	Date=${day}/${month}/${year}"
echo "SAUserDisputes	Location=$op_dir"
wget -O ${op_dir}/sauser${year}${month}${day}.csv $url

count=$(cat ${op_dir}/sauser${year}${month}${day}.csv | wc -l)
echo "SAUserDisputes	user_dispute_count=$(($count - 1))"
