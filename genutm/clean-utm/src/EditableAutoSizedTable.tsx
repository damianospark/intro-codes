import * as React from "react";
import Box from "@mui/material/Box";
import { DataGrid, GridCellParams, GridColDef, GridRowModel, GridValueGetterParams } from "@mui/x-data-grid";
import { useState, useEffect, MouseEventHandler } from "react";
import { Api } from "nocodb-sdk";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import clsx from "clsx";
import moment from "moment-timezone";
import { Tooltip } from '@mui/material';
import { FileCopyOutlined } from '@mui/icons-material';

import {
    GridToolbarContainer,
    GridToolbarExport,
    GridRowId,
    GridToolbarColumnsButton,
    GridToolbarDensitySelector,
    GridToolbarQuickFilter,
    MuiEvent,
} from "@mui/x-data-grid";
moment.locale("ko");

//  TODO: 타임스탬프는 모두 로컬 타임으로나오도록 Table 정의, 클라이언트내 로직 수정
interface UtmData {
    id: number;
    source: string;
    medium: string;
    campaign: string;
    term: string;
    content: string;
    land_url: string;
    post_url: string;
    descr: string;
    created_at: Date; // For date-time values, you can use 'string' or 'Date' type depending on your preference
    updated_at: Date; // For date-time values, you can use 'string' or 'Date' type depending on your preference
    creator_id: number | null;
    updater_id: number | null;
    budget: number | null;
    start_date: Date; //string | null; // For date values, you can use 'string' or 'Date' type depending on your preference
    end_date: Date; // | null; // For date values, you can use 'string' or 'Date' type depending on your preference
    target_location: string | null;
    target_audience: string | null;
}
const orgColumns: GridColDef[] = [
    {
        field: "id",
        headerName: "id",
        width: 20,
        editable: false,
        sortable: false,
    },
    {
        field: "utm",
        headerName: "UTM",
        width: 24,
        editable: false,
        sortable: false,
        renderCell: (params) => {
            const handleCopy = () => {
              navigator.clipboard.writeText(params.value);
            };
            return (
              <div>
                <Tooltip title="Copy UTM">
                  <IconButton size="small" onClick={handleCopy}>
                    <FileCopyOutlined />
                  </IconButton>
                </Tooltip>
                {/* {params.value} */}
              </div>
            );
          },
    },
    {
        field: "source",
        headerName: "source",
        minWidth: 10,
        maxWidth: 120,
        editable: false,
        sortable: true,
        hideable: false,
    },
    {
        field: "medium",
        headerName: "medium",
        minWidth: 170,
        editable: false,
        sortable: true,
        hideable: false,
    },
    {
        field: "campaign",
        headerName: "campaign",
        minWidth: 100,
        editable: false,
        sortable: true,
        hideable: false,
    },
    {
        field: "content",
        headerName: "content", //"광고 콘텐츠",
        minWidth: 100,
        editable: false,
        sortable: true,
    },
    {
        field: "term",
        headerName: "term", //"검색어 또는 키워드",
        minWidth: 100,
        editable: true,
        sortable: true,
    },

    {
        field: "land_url",
        headerName: "랜딩페이지 URL",
        minWidth: 100,
        editable: true,
        sortable: true,
    },
    {
        field: "post_url",
        headerName: "게시된 URL",
        minWidth: 240,
        editable: true,
        sortable: false,
    },
    {
        field: "descr",
        headerName: "설명",
        minWidth: 300,
        editable: true,
        sortable: false,
    },
    {
        field: "start_date",
        headerName: "광고시작일",
        minWidth: 110,
        editable: true,
        sortable: true,
        type: "date",
        valueGetter: (params: GridValueGetterParams) => new Date(params.row.start_date),
    },
    {
        field: "end_date",
        headerName: "광고종료일",
        minWidth: 120,
        editable: true,
        sortable: false,
        type: "date",
        valueGetter: (params: GridValueGetterParams) => new Date(params.row.end_date),
    },
    {
        field: "created_at",
        headerName: "생성일시",
        minWidth: 159,
        editable: false,
        sortable: true,
        type: "dateTime",
        valueGetter: (params: GridValueGetterParams) => new Date(params.row.created_at),
    },
    {
        field: "updated_at",
        headerName: "수정일시",
        minWidth: 159,
        editable: false,
        sortable: false,
        type: "dateTime",
        valueGetter: (params: GridValueGetterParams) => new Date(params.row.updated_at),
    },
    {
        field: "creator_id",
        headerName: "생성자ID",
        minWidth: 60,
        editable: false,
        sortable: true,
    },
    {
        field: "updater_id",
        headerName: "업데이트자 ID",
        minWidth: 100,
        editable: false,
        sortable: false,
    },
    {
        field: "budget",
        headerName: "광고 예산",
        minWidth: 100,
        editable: true,
        sortable: true,
    },

    {
        field: "target_location",
        headerName: "광고 대상 지역",
        minWidth: 100,
        editable: true,
        sortable: false,
    },
    {
        field: "target_audience",
        headerName: "광고 대상 고객군",
        minWidth: 100,
        editable: true,
        sortable: false,
    },
    
];

const columns = orgColumns.map((column) => ({
    ...column,
    cellClassName: (params: GridCellParams<any>) => {
        return clsx("super-app", { readonly: params.colDef.editable === false });
    },
}));

const CustomToolbar = (props: {
    handleDelete: MouseEventHandler<HTMLButtonElement> | undefined;
    hasSelectedRows: any;
    columns: GridColDef[];
    handleColumnVisibility: any;
    visibleColumns: GridColDef[];
}) => {
    // const CustomToolbar = ({ handleDelete:MouseEventHandler<HTMLButtonElement> , hasSelectedRows }) => {
    return (
        <GridToolbarContainer>
            <IconButton color="primary" aria-label="delete selected rows" onClick={props.handleDelete} disabled={!props.hasSelectedRows}>
                <DeleteIcon />
            </IconButton>
            <GridToolbarColumnsButton /> <GridToolbarDensitySelector /> <GridToolbarQuickFilter /> <GridToolbarExport />
        </GridToolbarContainer>
    );
};

const useFakeMutation = () => {
    return React.useCallback(
        (utmdata: Partial<UtmData>) =>
            new Promise<Partial<UtmData>>((resolve, reject) => {
                setTimeout(() => {
                    // if (utmdata.name?.trim() === "") {
                    //     reject(new Error("Error while saving user: name can't be empty."));
                    // } else {
                    //     resolve({ ...user, name: user.name?.toUpperCase() });
                    // }
                    console.log("utmdata", utmdata);

                    resolve({ ...utmdata });
                }, 200);
            }),
        []
    );
};

interface Props {
    client: any;
    createdId: number;
}
const EditableAutoSizedTable = ({ client, createdId }: Props) => {
    const [rows, setRows] = useState<UtmData[]>([]);
    const [selectedRows, setSelectedRows] = useState<GridRowId[]>([]);
    const [visibleColumns, setVisibleColumns] = useState(columns);
    const mutateRow = useFakeMutation();
    const [promiseArguments, setPromiseArguments] = React.useState<any>(null);

    useEffect(() => {
        const fetchData = async () => {
            const data = await client.dbTableRow.list("noco", "UtmGenerator", "utm_data");
            console.log("data==>", data);
            if (data) {
                setRows(data.list as UtmData[]);
            }
        };
        // if (rowId < 0)
        fetchData();
        // else{
        //     const data = await client.dbTableRow.list("noco", "UtmGenerator", "utm_data");

        // }
    }, [createdId]);

    const handleDelete = async () => {
        // const selectedRecords = rows.filter((record) => selectedIds.includes(record.id));
        const rowIds = rows
            .filter((row) => selectedRows.includes(row.id))
            .map((row) => {
                return { id: row.id };
            });

        setRows(rows.filter((row) => !selectedRows.includes(row.id)));

        const confirmation = window.confirm(`Are you sure you want to delete ${selectedRows.length} record(s)?`);
        if (confirmation) {
            // await Promise.all(selectedRows.map((record) => record.destroy()));

            const remainingRecords = rows.filter((record) => !selectedRows.includes(record.id));
            setRows([...remainingRecords]);
            console.log(rowIds);
            client.dbTableRow.bulkDelete("noco", "UtmGenerator", "utm_data", rowIds);
            setSelectedRows([]);
        }
    };
    const findChangedColumnName = (oldRow: GridRowModel, newRow: GridRowModel, columns: GridColDef[]): string | undefined => {
        for (let i = 0; i < columns.length; i++) {
            const field = columns[i].field;
            if (oldRow[field] !== newRow[field]) {
                return field;
            }
        }
        return undefined;
    };
    const processRowUpdate = React.useCallback(
        async (newRow: GridRowModel, oldRow: GridRowModel) => {
            // Find the difference between oldRow and newRow
            const changedColumnName = findChangedColumnName(oldRow, newRow, columns);
            const data: { [key: string]: any } = {};
            const response = await mutateRow(newRow);
            if (changedColumnName) {
                console.log("changedFields", changedColumnName, newRow[changedColumnName]);
                console.log("before : ", data);
                if (changedColumnName === "start_date" || changedColumnName === "end_date") {
                    data[changedColumnName] = moment(newRow[changedColumnName]).format("YYYY-MM-DD");
                } else {
                    data[changedColumnName] = newRow[changedColumnName];
                }
                client.dbTableRow.update("noco", "UtmGenerator", "utm_data", oldRow.id, data);
                console.log("after : ", data);
            }
            return response;
        },
        [mutateRow]
    );

    const handleProcessRowUpdateError = React.useCallback((error: Error) => {
        console.log(error.message);
        // setSnackbar({ children: error.message, severity: "error" });
    }, []);

    const handleColumnVisibility = (columnField: string) => {
        setVisibleColumns((prevVisibleColumns) => {
            const columnIndex = prevVisibleColumns.findIndex((col) => col.field === columnField);
            if (columnIndex > -1) {
                // Column is currently visible, so remove it
                return prevVisibleColumns.filter((col) => col.field !== columnField);
            } else {
                // Column is currently hidden, so add it
                const allColumns = columns;
                const newColumn = allColumns.find((col) => col.field === columnField);
                if (newColumn) {
                    return [...prevVisibleColumns, newColumn];
                } else {
                    return prevVisibleColumns;
                }
            }
        });
    };

    const hasSelectedRows = selectedRows.length > 0;

    return (
        // <Box sx={{ height: "100vh", width: "100%" }}>
        <Box
            sx={{
                height: "100vh",
                width: "100%",
                "& .super-app.readonly": {
                    backgroundColor: "rgba(255, 230, 230, 0.8)",
                    color: "#1a3e72",
                    fontWeight: "600",
                },
            }}
        >
            <DataGrid
                editMode="cell"
                rows={rows}
                columns={visibleColumns}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 20,
                        },
                    },
                    columns: {
                        columnVisibilityModel: {
                            id: false,
                            land_url: false,
                            //post_url: false,
                            updated_at: false,
                            updater_id: false,
                            budget: false,
                            target_location: false, //지역
                            target_audience: false, // 고객군
                        },
                    },
                }}
                pageSizeOptions={[20, 50, 100]}
                checkboxSelection
                disableRowSelectionOnClick
                // onSelectionModelChange={(newSelection: UtmData) => setSelectedRows(newSelection)}
                // onCellEditStop={handleEditCellChange}
                processRowUpdate={processRowUpdate}
                onProcessRowUpdateError={handleProcessRowUpdateError}
                components={{
                    Toolbar: CustomToolbar,
                }}
                componentsProps={{
                    toolbar: {
                        handleDelete,
                        hasSelectedRows,
                        columns,
                        handleColumnVisibility,
                        visibleColumns,
                    },
                }}
                onRowSelectionModelChange={(newSelectionModel) => {
                    // setSelectedRows(newSelection.selectionModel);
                    setSelectedRows(newSelectionModel.map((id) => id));
                }}
            />
            {/* {!!snackbar && (
        <Snackbar open onClose={handleCloseSnackbar} autoHideDuration={6000}>
          <Alert {...snackbar} onClose={handleCloseSnackbar} />
        </Snackbar> */}
        </Box>
    );
};
export default EditableAutoSizedTable;
