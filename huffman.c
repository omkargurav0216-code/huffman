#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TREE_HT 100

struct Node {
    char data;
    int freq;
    struct Node *left, *right;
};

struct MinHeap {
    int size;
    struct Node* array[256];
};

char codes[256][256];

struct Node* createNode(char data, int freq) {

    struct Node* node =
        (struct Node*)malloc(sizeof(struct Node));

    node->data = data;
    node->freq = freq;

    node->left = node->right = NULL;

    return node;
}

void swap(struct Node** a, struct Node** b) {

    struct Node* temp = *a;
    *a = *b;
    *b = temp;
}

void heapify(struct MinHeap* heap, int i) {

    int smallest = i;

    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < heap->size &&
        heap->array[left]->freq <
        heap->array[smallest]->freq)

        smallest = left;

    if (right < heap->size &&
        heap->array[right]->freq <
        heap->array[smallest]->freq)

        smallest = right;

    if (smallest != i) {

        swap(&heap->array[i],
             &heap->array[smallest]);

        heapify(heap, smallest);
    }
}

struct Node* extractMin(struct MinHeap* heap) {

    struct Node* temp = heap->array[0];

    heap->array[0] =
        heap->array[heap->size - 1];

    heap->size--;

    heapify(heap, 0);

    return temp;
}

void insertHeap(struct MinHeap* heap,
                struct Node* node) {

    int i = heap->size;

    heap->size++;

    while (i &&
           node->freq <
           heap->array[(i - 1) / 2]->freq) {

        heap->array[i] =
            heap->array[(i - 1) / 2];

        i = (i - 1) / 2;
    }

    heap->array[i] = node;
}

void buildHeap(struct MinHeap* heap) {

    int n = heap->size - 1;

    int i;

    for (i = (n - 1) / 2; i >= 0; i--)
        heapify(heap, i);
}

int isLeaf(struct Node* root) {

    return !(root->left) &&
           !(root->right);
}

struct Node* buildTree(char data[],
                       int freq[],
                       int size) {

    struct MinHeap heap;

    heap.size = size;

    int i;

    for (i = 0; i < size; i++) {
        heap.array[i] =
            createNode(data[i], freq[i]);
    }

    buildHeap(&heap);

    while (heap.size > 1) {

        struct Node* left =
            extractMin(&heap);

        struct Node* right =
            extractMin(&heap);

        struct Node* top =
            createNode('$',
                       left->freq + right->freq);

        top->left = left;
        top->right = right;

        insertHeap(&heap, top);
    }

    return extractMin(&heap);
}

void storeCodes(struct Node* root,
                int arr[],
                int top) {

    int i;

    if (root->left) {
        arr[top] = 0;
        storeCodes(root->left,
                   arr,
                   top + 1);
    }

    if (root->right) {
        arr[top] = 1;
        storeCodes(root->right,
                   arr,
                   top + 1);
    }

    if (isLeaf(root)) {

        for (i = 0; i < top; i++) {
            codes[(int)root->data][i] =
                arr[i] + '0';
        }

        codes[(int)root->data][top] = '\0';
    }
}

void generateJSON(struct Node* root, FILE* fp) {

    if (!root)
        return;

    fprintf(fp, "{");

    if (root->data != '$')
        fprintf(fp,
                "\"name\":\"%c(%d)\"",
                root->data,
                root->freq);

    else
        fprintf(fp,
                "\"name\":\"%d\"",
                root->freq);

    if (root->left || root->right) {

        fprintf(fp, ",\"children\":[");

        if (root->left)
            generateJSON(root->left, fp);

        if (root->right) {
            fprintf(fp, ",");
            generateJSON(root->right, fp);
        }

        fprintf(fp, "]");
    }

    fprintf(fp, "}");
}

int main(int argc, char* argv[]) {

    if (argc < 2) {
        printf("No Input");
        return 1;
    }

    char* text = argv[1];

    int freq[256] = {0};

    int i;

    for (i = 0; text[i]; i++)
        freq[(int)text[i]]++;

    char data[256];
    int frequencies[256];

    int size = 0;

    for (i = 0; i < 256; i++) {

        if (freq[i]) {

            data[size] = i;
            frequencies[size] = freq[i];

            size++;
        }
    }

    struct Node* root =
        buildTree(data,
                  frequencies,
                  size);

    int arr[MAX_TREE_HT];

    storeCodes(root, arr, 0);

    FILE* fp = fopen("tree.json", "w");

    generateJSON(root, fp);

    fclose(fp);

    printf("HUFFMAN CODES\n\n");

    for (i = 0; i < size; i++) {

        printf("%c : %s\n",
               data[i],
               codes[(int)data[i]]);
    }

    printf("\nENCODED TEXT\n\n");

    int compressedBits = 0;

    for (i = 0; text[i]; i++) {

        printf("%s",
               codes[(int)text[i]]);

        compressedBits +=
            strlen(codes[(int)text[i]]);
    }

    int originalBits = strlen(text) * 8;

    printf("\n\n");
printf("====================================\n");
printf("COMPRESSION STATISTICS\n");
printf("====================================\n");

printf("Original Size      : %d bits\n",
       originalBits);

printf("Compressed Size    : %d bits\n",
       compressedBits);

/* COMPRESSION RATIO */

float compressionRatio =
    ((float)compressedBits /
    originalBits) * 100;

printf("Compression Ratio  : %.2f%%\n",
       compressionRatio);

/* SPACE SAVED */

float saved =
    100 - compressionRatio;

printf("Space Saved        : %.2f%%\n",
       saved);

/* AVERAGE BITS PER CHARACTER */

float avgBits =
    (float)compressedBits /
    strlen(text);

printf("Average Bits/Char  : %.2f bits\n",
       avgBits);

printf("====================================\n");

    return 0;
}