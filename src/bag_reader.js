#!/usr/bin/env node

const fs = require('fs');
const Rosbag = require('rosbag');

let commonBuffer = new ArrayBuffer(8);

const typeLengths = [
  { length: 0, type: 'None', buffer: null, auxBuffer: null }, // None
  { length: 1, type: 'INT8', buffer: new Int8Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // INT8
  { length: 1, type: 'UINT8', buffer:  new Uint8Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // UINT8
  { length: 2, type: 'INT16', buffer: new Int16Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // INT16
  { length: 2, type: 'UINT16', buffer: new Uint16Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // UINT16
  { length: 4, type: 'INT32', buffer: new Int32Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // INT32
  { length: 4, type: 'UINT32', buffer: new Uint32Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // UINT32
  { length: 4, type: 'FLOAT32', buffer: new Float32Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // FLOAT32
  { length: 8, type: 'FLOAT64', buffer: new Float64Array(commonBuffer), auxBuffer: new Uint8Array(commonBuffer) }, // FLOAT64
  { length: 0, type: 'None', buffer: null, auxBuffer: null }  // None
];

// Transform ROSBAG file to PCD files
class RosBagReader {
  async convert(from, to) {
    let bag = await Rosbag.open(from), idx = 0;

    await bag.readMessages({}, (result) => {
      if (result && typeof result.chunkOffset === 'number'
      && typeof result.totalChunks === 'number' && result.message
      && result.message.fields && result.message.data
      && result.message.point_step
      ) {

        let writeStream = fs.createWriteStream(`${to}/${idx}.pcd` );

        let points = [];
        let mainPointer = 0;

        while (mainPointer < result.message.data.length) {
          let point = {};
          result.message.fields.forEach((field) => {
            for (let i = 0; i < typeLengths[field.datatype].length; i++) {
              typeLengths[field.datatype].auxBuffer[i] = result.message.data[mainPointer + field.offset + i];
            }
            point[field.name] = typeLengths[field.datatype].buffer[0];
          });

          points.push(point);
          mainPointer += result.message.point_step;
        }

        writeStream.write("VERSION .7\n");
        writeStream.write("FIELDS x y z intensity\n");
        writeStream.write("SIZE 4 4 4 1\n")
        writeStream.write("TYPE F F F U\n")
        writeStream.write("COUNT 1 1 1 1\n")
        writeStream.write(`WIDTH ${points.length}\n`)
        writeStream.write("HEIGHT 1\n")
        writeStream.write(`POINTS ${points.length}\n`)
        writeStream.write("DATA binary\n")

        let offset = 0

        let b = Buffer.alloc( points.length * (4 * 3 + 1)  );

        points.forEach((point) => {
          b.writeFloatLE(point.x || 0, offset + 0);
          b.writeFloatLE(point.y || 0, offset + 4);
          b.writeFloatLE(point.z || 0, offset + 8);
          b.writeUInt8(point.intensity || 0, offset + 12);
          offset += (4 * 3 + 1)
        })
        writeStream.write(b)

        // close the stream
        writeStream.end();

        idx+=1;
      }
    })
  }

}

module.exports = RosBagReader;

let input  = process.argv[2];
let output = process.argv[3];

new RosBagReader().convert(input, output)
