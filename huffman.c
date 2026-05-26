#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TREE_HT 100

struct MinHeapNode {
    char data;
    unsigned freq;
    struct MinHeapNode *left, *right;
};

struct MinHeap {
    unsigned size;
    unsigned capacity;
    struct MinHeapNode** array;
};

struct MinHeapNode* newNode(char data, unsigned freq) {
    struct MinHeapNode* temp =
        (struct MinHeapNode*)malloc(sizeof(struct MinHeapNode));

    temp->left = temp->right = NULL;
    temp->data = data;
    temp->freq = freq;

    return temp;
}

struct MinHeap* createMinHeap(unsigned capacity) {

    struct MinHeap* minHeap =
        (struct MinHeap*)malloc(sizeof(struct MinHeap));

    minHeap->size = 0;
    minHeap->capacity = capacity;

    minHeap->array =
        (struct MinHeapNode**)malloc(
            minHeap->capacity * sizeof(struct MinHeapNode*));

    return minHeap;
}

void swapMinHeapNode(
    struct MinHeapNode** a,
    struct MinHeapNode** b) {

    struct MinHeapNode* t = *a;
    *a = *b;
    *b = t;
}

void minHeapify(struct MinHeap* minHeap, int idx) {

    int smallest = idx;
    int left = 2 * idx + 1;
    int right = 2 * idx + 2;

    if (left < minHeap->size &&
        minHeap->array[left]->freq <
        minHeap->array[smallest]->freq)

        smallest = left;

    if (right < minHeap->size &&
        minHeap->array[right]->freq <
        minHeap->array[smallest]->freq)

        smallest = right;

    if (smallest != idx) {

        swapMinHeapNode(
            &minHeap->array[smallest],
            &minHeap->array[idx]);

        minHeapify(minHeap, smallest);
    }
}

int isSizeOne(struct MinHeap* minHeap) {
    return (minHeap->size == 1);
}

struct MinHeapNode* extractMin(struct MinHeap* minHeap) {

    struct MinHeapNode* temp = minHeap->array[0];

    minHeap->array[0] =
        minHeap->array[minHeap->size - 1];

    --minHeap->size;

    minHeapify(minHeap, 0);

    return temp;
}

void insertMinHeap(
    struct MinHeap* minHeap,
    struct MinHeapNode* minHeapNode) {

    ++minHeap->size;

    int i = minHeap->size - 1;

    while (i &&
           minHeapNode->freq <
           minHeap->array[(i - 1) / 2]->freq) {

        minHeap->array[i] =
            minHeap->array[(i - 1) / 2];

        i = (i - 1) / 2;
    }

    minHeap->array[i] = minHeapNode;
}

void buildMinHeap(struct MinHeap* minHeap) {

    int n = minHeap->size - 1;

    int i;

    for (i = (n - 1) / 2; i >= 0; --i)
        minHeapify(minHeap, i);
}

int isLeaf(struct MinHeapNode* root) {
    return !(root->left) && !(root->right);
}

struct MinHeap* createAndBuildMinHeap(
    char data[],
    int freq[],
    int size) {

    struct MinHeap* minHeap = createMinHeap(size);

    int i;

    for (i = 0; i < size; ++i)
        minHeap->array[i] =
            newNode(data[i], freq[i]);

    minHeap->size = size;

    buildMinHeap(minHeap);

    return minHeap;
}

struct MinHeapNode* buildHuffmanTree(
    char data[],
    int freq[],
    int size) {

    struct MinHeapNode *left, *right, *top;

    struct MinHeap* minHeap =
        createAndBuildMinHeap(data, freq, size);

    while (!isSizeOne(minHeap)) {

        left = extractMin(minHeap);
        right = extractMin(minHeap);

        top = newNode('$',
                      left->freq + right->freq);

        top->left = left;
        top->right = right;

        insertMinHeap(minHeap, top);
    }

    return extractMin(minHeap);
}

char codes[256][256];

void storeCodes(struct MinHeapNode* root,
                int arr[],
                int top) {

    int i;

    if (root->left) {
        arr[top] = 0;
        storeCodes(root->left, arr, top + 1);
    }

    if (root->right) {
        arr[top] = 1;
        storeCodes(root->right, arr, top + 1);
    }

    if (isLeaf(root)) {

        for (i = 0; i < top; ++i) {
            codes[(int)root->data][i] =
                arr[i] + '0';
        }

        codes[(int)root->data][top] = '\0';
    }
}

int main(int argc, char *argv[]) {

    if (argc < 2) {
        printf("No input provided\n");
        return 1;
    }

    char *text = argv[1];

    int freq[256] = {0};

    int i;

    for (i = 0; text[i] != '\0'; i++) {
        freq[(int)text[i]]++;
    }

    char data[256];
    int frequencies[256];
    int size = 0;

    for (i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            data[size] = (char)i;
            frequencies[size] = freq[i];
            size++;
        }
    }

    struct MinHeapNode* root =
        buildHuffmanTree(data,
                         frequencies,
                         size);

    int arr[MAX_TREE_HT], top = 0;

    storeCodes(root, arr, top);

    printf("HUFFMAN CODES\n\n");

    for (i = 0; i < size; i++) {
        printf("%c : %s\n",
               data[i],
               codes[(int)data[i]]);
    }

    printf("\nENCODED TEXT\n\n");

    int compressedBits = 0;

    for (i = 0; text[i] != '\0'; i++) {

        printf("%s",
               codes[(int)text[i]]);

        compressedBits +=
            strlen(codes[(int)text[i]]);
    }

    int originalBits = strlen(text) * 8;

    printf("\n\n");

    printf("Original Size : %d bits\n",
           originalBits);

    printf("Compressed Size : %d bits\n",
           compressedBits);

    float ratio =
        ((float)(originalBits - compressedBits)
        / originalBits) * 100;

    printf("Compression Saved : %.2f%%\n",
           ratio);

    return 0;
}