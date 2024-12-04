all: reset

clear-errs:
	@echo "Removing logs"
	-@rm ./*errors.log
	-@rm ./logs/*errors.log
	-@rm ./src/logs/*errors.log

kill:
	-pgrep -u jdolak python3
	-pkill -u jdolak python3

reset: kill clear-errs