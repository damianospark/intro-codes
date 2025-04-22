import * as React from "react";
import { alpha } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Checkbox from "@mui/material/Checkbox";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import DeleteIcon from "@mui/icons-material/Delete";
import CopyAllIcon from "@mui/icons-material/CopyAll";
import { visuallyHidden } from "@mui/utils";

import Stack from "@mui/material/Stack";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import { CardActionArea } from "@mui/material";
// import ClipboardJS from "clipboard";

export interface Data {
    course: string;
    distance: number;
    duration: number;
    durastr: string;
    avgspeed: number;
    visit: number;
    deliver: number;
    date: string;
    method: string;
}
const todayStr = new Date().toLocaleDateString().split("/").join("/");

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
    if (b[orderBy] < a[orderBy]) {
        return -1;
    }
    if (b[orderBy] > a[orderBy]) {
        return 1;
    }
    return 0;
}

type Order = "asc" | "desc";

function getComparator<Key extends keyof any>(
    order: Order,
    orderBy: Key
): (a: { [key in Key]: number | string }, b: { [key in Key]: number | string }) => number {
    return order === "desc" ? (a, b) => descendingComparator(a, b, orderBy) : (a, b) => -descendingComparator(a, b, orderBy);
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number) {
    const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
    stabilizedThis.sort((a, b) => {
        const order = comparator(a[0], b[0]);
        if (order !== 0) {
            return order;
        }
        return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
}

interface HeadCell {
    disablePadding: boolean;
    id: keyof Data;
    label: string;
    numeric: boolean;
}

const headCells: readonly HeadCell[] = [
    {
        id: "course",
        numeric: false,
        disablePadding: true,
        label: "운행코스",
    },
    {
        id: "distance",
        numeric: true,
        disablePadding: false,
        label: "운행거리(km)",
    },
    {
        id: "duration",
        numeric: true,
        disablePadding: false,
        label: "소요시간",
    },
    {
        id: "durastr",
        numeric: false,
        disablePadding: false,
        label: "시간차",
    },
    {
        id: "avgspeed",
        numeric: true,
        disablePadding: false,
        label: "평균속도(km/h)",
    },
    {
        id: "visit",
        numeric: true,
        disablePadding: false,
        label: "방문장소",
    },
    {
        id: "deliver",
        numeric: true,
        disablePadding: false,
        label: "배달건수",
    },
    {
        id: "method",
        numeric: false,
        disablePadding: true,
        label: "배차방법",
    },
];

interface EnhancedTableProps {
    numSelected: number;
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof Data) => void;
    onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
}

function EnhancedTableHead(props: EnhancedTableProps) {
    const { onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort } = props;
    const createSortHandler = (property: keyof Data) => (event: React.MouseEvent<unknown>) => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {/* <TableCell padding="checkbox">
                    <Checkbox
                        color="primary"
                        indeterminate={numSelected > 0 && numSelected < rowCount}
                        checked={rowCount > 0 && numSelected === rowCount}
                        onChange={onSelectAllClick}
                        inputProps={{
                            "aria-label": "select all desserts",
                        }}
                    />
                </TableCell> */}
                {headCells.map((headCell) => (
                    <TableCell
                        key={headCell.id}
                        // align={headCell.numeric ? "right" : "left"}
                        align={"center"}
                        padding={headCell.disablePadding ? "none" : "normal"}
                        sortDirection={orderBy === headCell.id ? order : false}
                    >
                        <TableSortLabel
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order : "asc"}
                            onClick={createSortHandler(headCell.id)}
                        >
                            {headCell.label}
                            {orderBy === headCell.id ? (
                                <Box component="span" sx={visuallyHidden}>
                                    {order === "desc" ? "sorted descending" : "sorted ascending"}
                                </Box>
                            ) : null}
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

interface EnhancedTableToolbarProps {
    numSelected: number;
    summaryCsv: string;
    // setToClip: (scsv: string) => void;
}

function EnhancedTableToolbar(props: EnhancedTableToolbarProps) {
    const { numSelected } = props;
    const handleCopy = () => {
        navigator.clipboard.writeText(props.summaryCsv);
    };
    // React.useEffect(() => {
    //     // const clipboard = new ClipboardJS(".btn");
    //     // clipboard.destroy();
    //     return () => {
    //         // clipboard.destroy();
    //     };}, []);

    // const handleCopy = () => {
    //     const dummy = document.createElement("textarea");
    //     dummy.value=props.summaryCsv
    //     dummy.style.position="fixed"
    //     document.body.appendChild(dummy);
    //     dummy.focus()
    //     dummy.select();
    //     console.log(dummy);
    //     const copied=document.execCommand("copy");
    //     console.log('copied ---------- \n', copied)
    //     document.body.removeChild(dummy);
    // };

    return (
        <Toolbar
            sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
                ...(numSelected > 0 && {
                    bgcolor: (theme) => alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
                }),
            }}
        >
            {numSelected > 0 ? (
                <Typography sx={{ flex: "1 1 100%" }} color="inherit" variant="subtitle1" component="div">
                    {numSelected} selected
                </Typography>
            ) : (
                <Typography sx={{ flex: "1 1 100%" }} variant="h6" id="tableTitle" component="div">
                    {todayStr} 배차 계획 요약
                </Typography>
            )}
            {numSelected > 0 ? (
                <Tooltip title="Delete">
                    <IconButton>
                        <DeleteIcon />
                    </IconButton>
                </Tooltip>
            ) : (
                <Tooltip title="Filter list">
                    <IconButton className="btn" aria-label="CopyAll" color="primary" onClick={handleCopy}>
                        <CopyAllIcon />
                    </IconButton>
                </Tooltip>
            )}
        </Toolbar>
    );
}

type Props = {
    route_info: Data[];
};

const Papa = require("papaparse");

// export default function EnhancedTable({ values }) {
const EnhancedTable: React.FC<Props> = ({ route_info }: Props) => {
    const [order, setOrder] = React.useState<Order>("asc");
    const [orderBy, setOrderBy] = React.useState<keyof Data>("distance");
    const [selected, setSelected] = React.useState<readonly string[]>([]);
    const [page, setPage] = React.useState(0);
    const [dense, setDense] = React.useState(false);
    const [rowsPerPage, setRowsPerPage] = React.useState(5);

    if (!route_info || !route_info.length) {
        return (
            <Stack direction="row" justifyContent="center">
                <Card sx={{ maxWidth: 345 }}>
                    <CardActionArea>
                        <CardMedia
                            component="img"
                            height="140"
                            image="https://mui.com/static/images/cards/contemplative-reptile.jpg"
                            alt="green iguana"
                        />
                        <CardContent>
                            <Typography gutterBottom variant="h5" component="div">
                                배차 미 진행
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                자동또는 수동 배차를 수행한 뒤 열면 전체 경로의 예상 요약 정보를 볼 수 있습니다.
                                <br /> <b>화이팅!!</b>{" "}
                            </Typography>
                        </CardContent>
                    </CardActionArea>
                </Card>
            </Stack>
        );
    }

    const rows = route_info;
    // const newRows = route_info.map((route) => { return {...route,  date:todayStr}});
    const rowsCsv = Papa.unparse(rows, { header: true, delimiter: "\t" });
    const handleRequestSort = (event: React.MouseEvent<unknown>, property: keyof Data) => {
        const isAsc = orderBy === property && order === "asc";
        setOrder(isAsc ? "desc" : "asc");
        setOrderBy(property);
    };

    const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            const newSelected = rows.map((n) => n.course);
            setSelected(newSelected);
            return;
        }
        setSelected([]);
    };

    const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
        const selectedIndex = selected.indexOf(name);
        let newSelected: readonly string[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, name);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selected.slice(1));
        } else if (selectedIndex === selected.length - 1) {
            newSelected = newSelected.concat(selected.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
        }

        setSelected(newSelected);
    };

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleChangeDense = (event: React.ChangeEvent<HTMLInputElement>) => {
        setDense(event.target.checked);
    };

    const isSelected = (name: string) => selected.indexOf(name) !== -1;

    // Avoid a layout jump when reaching the last page with empty rows.
    const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

    return (
        <Box sx={{ width: "100%" }}>
            <Paper sx={{ width: "100%", mb: 2 }}>
                <EnhancedTableToolbar numSelected={selected.length} summaryCsv={rowsCsv} />
                <TableContainer>
                    <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size={dense ? "small" : "medium"}>
                        <EnhancedTableHead
                            numSelected={selected.length}
                            order={order}
                            orderBy={orderBy}
                            onSelectAllClick={handleSelectAllClick}
                            onRequestSort={handleRequestSort}
                            rowCount={rows.length}
                        />
                        <TableBody>
                            {stableSort(rows, getComparator(order, orderBy))
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((row, index) => {
                                    const isItemSelected = isSelected(row.course);
                                    const labelId = `enhanced-table-checkbox-${index}`;
                                    const colors = [
                                        "#ff5348",
                                        "#8530f8",
                                        "#0eaecc",
                                        "#ef6fe9",
                                        "#15a84b",
                                        "#0304d0",
                                        "#6e7816",
                                        "#130553",
                                        "#4fcfef",
                                        "#ff9905",
                                    ];
                                    // const colors = ['#ffa8af', '#b794fc', '#4aeada', '#ffaffc', '#34eb8e', '#3659f4', '#9fbb8a', '#373886', '#11f1f1', '#cc9900']

                                    const bgc = colors[row.course.charCodeAt(0) - "A".charCodeAt(0)];

                                    return (
                                        <TableRow
                                            hover
                                            onClick={(event) => handleClick(event, row.course)}
                                            role="checkbox"
                                            aria-checked={isItemSelected}
                                            tabIndex={-1}
                                            key={row.course}
                                            selected={isItemSelected}
                                        >
                                            {/* <TableCell padding="checkbox">
                                                <Checkbox
                                                    color="primary"
                                                    checked={isItemSelected}
                                                    inputProps={{
                                                        "aria-labelledby": labelId,
                                                    }}
                                                />
                                            </TableCell> */}
                                            <TableCell
                                                component="th"
                                                id={labelId}
                                                scope="row"
                                                padding="none"
                                                align="center"
                                                sx={{ backgroundColor: `${bgc}` }}
                                            >
                                                {row.course}
                                            </TableCell>
                                            <TableCell align="center">{row.distance}</TableCell>
                                            <TableCell align="center">{row.duration}</TableCell>
                                            <TableCell align="center">{row.durastr}</TableCell>
                                            <TableCell align="center">{row.avgspeed}</TableCell>
                                            <TableCell align="center">{row.visit}</TableCell>
                                            <TableCell align="center">{row.deliver}</TableCell>
                                            <TableCell align="center">{row.method}</TableCell>
                                        </TableRow>
                                    );
                                })}
                            {emptyRows > 0 && (
                                <TableRow
                                    style={{
                                        height: (dense ? 33 : 53) * emptyRows,
                                    }}
                                >
                                    <TableCell colSpan={6} />
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={rows.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </Paper>
            <FormControlLabel control={<Switch checked={dense} onChange={handleChangeDense} />} label="Dense padding" />
        </Box>
    );
};

export default EnhancedTable;
