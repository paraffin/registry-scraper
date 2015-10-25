.PHONY: \
		install-ack \
		review-tech-debt \
		count-tech-debt

ACK_BIN := $(shell which ack)
ACK := ack -ri --ignore-dir=.git --ignore-dir=tests/tech-debt

install-ack:
ifeq ('$(ACK_BIN)','')
	sudo apt-get install -y ack-grep
endif

review-tech-debt: install-ack
	@$(ACK) -A 5 '# YELLOW' . || true
	@$(ACK) -A 5 '# ORANGE' . || true
	@$(ACK) -A 5 '# RED' . || true

test-tech-debt: review-tech-debt install-ack
	@$(info Tech debt totals:)
	@$(info Yellow: $(shell $(ACK) '# YELLOW' . | wc -l))
	@$(info Orange: $(shell $(ACK) '# ORANGE' . | wc -l))
	@$(info Red: $(shell $(ACK) '# RED' . | wc -l))
	@if $(ACK) '# RED' . ; then \
	  	echo "You have RED tech debt! Please don't merge this!"; \
		exit 2; \
	fi
