clear-errs:
	rm ./*errors.log

kill:
	pgrep -u jdolak python3
	pkill -u jdolak python3