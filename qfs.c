int RefPackDecompress(const struct RefPackStream * Stream, const unsigned char * inbuffer, unsigned char * outbuffer){
    /* Returns 0x00 on success,
        0x01 if a parameter is invalid,
        0xF1 if the opcode did not finish,
        0xF3 if some data still had yet to be decompressed when the end of the compressed stream was reached,
        or 0xF5 if more data in the compressed stream existed when all required data was decompressed. */

    unsigned int StreamSize = Stream->RefPackHeader.CompressedFileSize, Decompresseddataleft = Stream->RefPackHeader.DecompressedDataSize;
    unsigned int offset = 0; /* Offset relative to the input stream; it cannot determine the data written in the output stream, so we must keep a dedicated variable for that */
    unsigned int datawritten = 0;
    int stopflag = 0;

    /* Leave if a parameter is invalid */
    if(Stream == NULL || inbuffer == NULL || outbuffer == NULL)
        return 0x01;

    while(offset < StreamSize && !stopflag){
        unsigned char currentbyte;
        unsigned int ProceedingDataLength, ReferencedDataLength, ReferencedDataOffset;

        /****
          Fetch the opcode
        */

        /* The first byte determines the size of the entire opcode.
           In some cases, that one byte is it, but the size in other cases can be up to 4 bytes. */

        currentbyte = *(inbuffer++), offset++;
        if(currentbyte <= 0x7F){ /* 2 bytes */
            if(Decompresseddataleft < 1) return 0xF1;

            /* First byte */
            ProceedingDataLength = currentbyte & 0x03;
            ReferencedDataLength = ((currentbyte & 0x1C) >> 2) + 3;
            ReferencedDataOffset = (currentbyte & 0x60) << 3;

            /* Second byte */
            currentbyte = *(inbuffer++);
            ReferencedDataOffset += currentbyte;

            offset++;
        }else if(currentbyte <= 0xBF){ /* 3 bytes */
            if(Decompresseddataleft < 2) return 0xF1;

            /* First byte */
            ReferencedDataLength = (currentbyte & 0x3F) + 4;

            /* Second byte */
            currentbyte = *(inbuffer++);
            ProceedingDataLength = (currentbyte & 0xC0) >> 6;
            ReferencedDataOffset = (currentbyte & 0x3F) << 8;

            /* Third byte */
            currentbyte = *(inbuffer++);
            ReferencedDataOffset += currentbyte;

            offset += 2;
        }else if(currentbyte <= 0xDF){ /* 4 bytes */
            if(Decompresseddataleft < 1) return 0xF1;

            /* First byte */
            ProceedingDataLength = currentbyte & 0x03;
            ReferencedDataLength = ((currentbyte & 0x0C) << 6) + 5;
            ReferencedDataOffset = (currentbyte & 0x10) << 12;

            /* Second byte */
            currentbyte = *(inbuffer++);
            ReferencedDataOffset += currentbyte << 8;

            /* Third byte */
            currentbyte = *(inbuffer++);
            ReferencedDataOffset += currentbyte;

            /* Fourth byte */
            currentbyte = *(inbuffer++);
            ReferencedDataLength += currentbyte;

            offset += 3;
        }else{ /* 1 byte: Two different opcode types fall into this category */
            if(currentbyte <= 0xFB){
                ProceedingDataLength = ((currentbyte & 0x1F) << 2) + 4;
            }else{
                ProceedingDataLength = currentbyte & 0x03;
                stopflag++;
            }
            ReferencedDataLength = 0;
            ReferencedDataOffset = 0;
        }

        /****
          Copy proceeding data
        */

        if(ProceedingDataLength != 0){
            if(ProceedingDataLength > Decompresseddataleft){
                if(!Decompresseddataleft) return 0xF3;
                ProceedingDataLength = Decompresseddataleft;
            }
            
            memcpy(outbuffer, inbuffer, ProceedingDataLength);
            Decompresseddataleft    -= ProceedingDataLength;
            datawritten             += ProceedingDataLength;
            offset      += ProceedingDataLength;
            inbuffer    += ProceedingDataLength;
            outbuffer   += ProceedingDataLength;
        }

        /****
          Copy referenced data
        */

        if(ReferencedDataLength != 0){
            unsigned int copylength, nulllength = 0;
            ReferencedDataOffset++; /* An offset of 0 would mean to refer to the (uninitialized?) spot that you're writing at, which is not supposed to contain any data. */
            if(ReferencedDataLength > Decompresseddataleft){
                if(!Decompresseddataleft) return 0xF5;
                ReferencedDataLength = Decompresseddataleft;
            }

            copylength = (ReferencedDataLength > ReferencedDataOffset) ? ReferencedDataOffset : ReferencedDataLength;

            /* We need to check for the instance that the given offset is behind our write buffer.
               When this occurs, the decoder is to treat the data as if it is all null. */
            if(ReferencedDataOffset > datawritten){
                nulllength = ReferencedDataOffset - datawritten; /* This is the number of null bytes that the offset extends into */
                #ifdef FAR_DEBUG
                printf("Null copy: Specified offset is: %lu, yet data written so far is: %lu", ReferencedDataOffset, datawritten);
                #endif
                if(nulllength > ReferencedDataLength) nulllength = ReferencedDataLength; /* But it doesn't mean that we will use all of it. */

                memset(outbuffer, 0x00, nulllength); 
                outbuffer += nulllength; /* If we still have more to copy over, outbuffer-ReferencedDataOffset points to the first real byte in the reference buffer, now. */
                if(copylength > nulllength) copylength -= nulllength; else copylength = 0;
            }

            /* It is possible that the offset specified by the stream does not provide for a large enough buffer to copy from.
               This event would be caused by the reference data offset (relative from the end of the out buffer) being set smaller than can add with the proceeding data length to meet the reference data length.
               When this occurs, the decoder is to repeatedly copy the referenced data (from the beginning again) until the reference copy's length is satisfied. */

            /* We will do this in a way so that we call memcpy ceil(log2(N)) times instead of N times.
               The performance will only increase by the amount we reduce argument pushing and memcpy startup, but whatever */


            if(copylength){
                /* Copying from the source at ReferencedDataOffset */
                unsigned int datacopied = nulllength;
                unsigned char * copysource = outbuffer-nulllength;
                memcpy(outbuffer, outbuffer-ReferencedDataOffset, copylength);
                outbuffer += copylength;
                datacopied += copylength;

                for(copylength = copylength+nulllength; copylength; copylength <<= 1){
                    /* Copying from what we have in the out buffer, repeatedly until all the data has been copied */

                    if(copylength > ReferencedDataLength - datacopied){
                        copylength = ReferencedDataLength - datacopied;
                        if(!copylength) break;
                    }

                    memcpy(outbuffer, copysource, copylength);
                    outbuffer += copylength;
                    datacopied += copylength;
                }
            }

            Decompresseddataleft    -= ReferencedDataLength;
            datawritten             += ReferencedDataLength;
        }
    }
    return (Decompresseddataleft) ? 0xF3 : 0;
}
