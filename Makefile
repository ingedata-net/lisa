SRC_DIR=./src
PROTO_SRC_DIR=./proto
PROTO_DST_DIR=$(SRC_DIR)/lisa/proto

proto: lisa.proto

lisa.proto:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/lisa.proto

